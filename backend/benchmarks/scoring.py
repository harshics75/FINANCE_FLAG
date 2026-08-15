"""Deterministic, structural scoring — no extra LLM calls (an LLM-judge layer would
double API usage against an already-tight free-tier quota for marginal benefit at this
scale). Two honest limits worth stating up front, not burying:

1. "hallucination_flag" here is a coarse heuristic proxy — it flags when the response
   references an entity (a company name) that wasn't in the scenario it was given. It
   is NOT true hallucination detection (that needs a judge model or human review) and
   will miss subtler fabrications. Treat it as a signal, not a verdict.
2. reasoning/action quality scores are heuristics (length, specificity markers, internal
   consistency) — a reasonable proxy for "did this engage with the actual scenario," not
   a substitute for a human or expert reading the transcripts.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from benchmarks.dataset import COMPANIES
from benchmarks.storage import ScoreRecord

REQUIRED_FIELDS = {
    "flag_raised": bool,
    "risk_score": (int, float),
    "category": str,
    "priority": str,
    "reasoning": str,
    "recommended_action": str,
    "confidence": (int, float),
}
VALID_CATEGORIES = {"revenue", "cash_flow", "expenses", "receivables", "inventory",
                    "compliance", "audit", "macro", "other"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}
CAUSAL_MARKERS = ["due to", "because", "driven by", "as a result", "given that",
                  "caused by", "reflects", "stems from", "attributable to"]
ACTION_VERBS = ["review", "escalate", "audit", "renegotiate", "follow up", "investigate",
               "monitor closely", "flag for", "reassess", "verify", "engage", "tighten",
               "accelerate", "collect", "notify"]
GENERIC_ACTION_PHRASES = ["monitor the situation", "keep an eye", "watch closely", "stay informed"]


def _extract_json(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[4:] if text.lower().startswith("json") else text
    for candidate in (text, _balanced_braces(text)):
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            continue
    return None


def _balanced_braces(text: str) -> str | None:
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def _check_schema(parsed: dict) -> tuple[bool, list[str]]:
    missing = []
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in parsed:
            missing.append(field)
        elif not isinstance(parsed[field], expected_type):
            missing.append(f"{field}(wrong type)")
    return (len(missing) == 0), missing


def _reasoning_score(parsed: dict, prompt: str) -> float:
    reasoning = str(parsed.get("reasoning", ""))
    if not reasoning:
        return 0.0
    words = len(reasoning.split())
    length_score = min(4.0, words / 15)  # up to 4 pts for substantive length (~60+ words)
    causal_score = 3.0 if any(m in reasoning.lower() for m in CAUSAL_MARKERS) else 0.0
    # Grounding: does the reasoning reference actual numbers from the scenario it was given?
    prompt_numbers = set(re.findall(r"\d+\.?\d*", prompt))
    reasoning_numbers = set(re.findall(r"\d+\.?\d*", reasoning))
    grounded_score = 3.0 if (prompt_numbers & reasoning_numbers) else 0.0
    return round(min(10.0, length_score + causal_score + grounded_score), 2)


def _risk_explanation_score(parsed: dict) -> float:
    reasoning = str(parsed.get("reasoning", "")).lower()
    risk_score = parsed.get("risk_score")
    priority = str(parsed.get("priority", "")).lower()
    if not isinstance(risk_score, (int, float)):
        return 0.0
    score = 0.0
    # Internal consistency: does the stated priority match the numeric risk_score band?
    expected = ("critical" if risk_score >= 80 else "high" if risk_score >= 60
               else "medium" if risk_score >= 30 else "low")
    if priority == expected:
        score += 5.0
    elif priority in VALID_PRIORITIES:
        score += 1.0  # valid label, just inconsistent with the score
    # Does the reasoning actually mention risk/flag language at all?
    if any(w in reasoning for w in ("risk", "flag", "concern", "exposure", "warrant")):
        score += 5.0
    return round(min(10.0, score), 2)


def _action_quality(parsed: dict) -> float:
    action = str(parsed.get("recommended_action", "")).strip()
    if not action:
        return 0.0
    lower = action.lower()
    if any(g in lower for g in GENERIC_ACTION_PHRASES) and len(action.split()) < 8:
        return 2.0  # boilerplate, low-effort
    score = 3.0 if len(action.split()) >= 6 else 1.0
    score += 4.0 if any(v in lower for v in ACTION_VERBS) else 0.0
    score += 3.0 if len(action) > 40 else 0.0
    return round(min(10.0, score), 2)


def _hallucination_flag(parsed: dict, prompt: str) -> bool:
    """Heuristic proxy only — see module docstring. Flags if the reasoning names a
    company from our known roster that ISN'T the one actually in the scenario."""
    reasoning = str(parsed.get("reasoning", ""))
    prompt_companies = {c for c in COMPANIES if c in prompt}
    mentioned = {c for c in COMPANIES if c in reasoning}
    fabricated = mentioned - prompt_companies
    return len(fabricated) > 0


def score_response(request_id: str, raw_response: str | None, prompt: str) -> ScoreRecord:
    if raw_response is None:
        return ScoreRecord(request_id=request_id, json_valid=False, schema_compliant=False,
                           missing_fields="no_response", reasoning_score=0, risk_explanation_score=0,
                           priority_accuracy=0, action_quality=0, hallucination_flag=False, overall_score=0)

    parsed = _extract_json(raw_response)
    if parsed is None:
        return ScoreRecord(request_id=request_id, json_valid=False, schema_compliant=False,
                           missing_fields="unparseable", reasoning_score=0, risk_explanation_score=0,
                           priority_accuracy=0, action_quality=0, hallucination_flag=False, overall_score=0)

    schema_ok, missing = _check_schema(parsed)
    category_ok = str(parsed.get("category", "")).lower() in VALID_CATEGORIES
    priority_valid = str(parsed.get("priority", "")).lower() in VALID_PRIORITIES
    if not category_ok:
        missing.append("category(invalid enum)")
    if not priority_valid:
        missing.append("priority(invalid enum)")

    reasoning_score = _reasoning_score(parsed, prompt)
    risk_score = _risk_explanation_score(parsed)
    priority_accuracy = 10.0 if priority_valid and category_ok else 3.0 if priority_valid else 0.0
    action_score = _action_quality(parsed)
    hallucinated = _hallucination_flag(parsed, prompt)

    overall = (reasoning_score * 0.3 + risk_score * 0.25 + action_score * 0.2 +
              priority_accuracy * 0.15 + (10 if schema_ok else 0) * 0.1)
    if hallucinated:
        overall = max(0.0, overall - 3.0)  # penalize, don't zero out — it's a heuristic signal

    return ScoreRecord(
        request_id=request_id, json_valid=True, schema_compliant=schema_ok,
        missing_fields=",".join(missing), reasoning_score=reasoning_score,
        risk_explanation_score=risk_score, priority_accuracy=priority_accuracy,
        action_quality=action_score, hallucination_flag=hallucinated,
        overall_score=round(overall, 2),
    )
