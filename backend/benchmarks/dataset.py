"""Synthetic finance-flagging scenario generator. Template + parameter substitution,
seeded for reproducibility, so the same --mode always yields the identical case set
(required for --resume to line up, and for fair before/after comparisons).

Every case shares ONE task instruction and ONE required JSON output schema — only the
scenario content varies by category. This mirrors how the app's own agents/graph.py
prompts work (fixed schema, varying financial content) and is what makes cross-model
comparison meaningful: same ask, same contract, different model.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

from benchmarks.storage import CaseRecord

MODE_SIZES = {"small": 60, "medium": 300, "large": 1000}

CATEGORIES = [
    "bullish", "bearish", "mixed_signals", "macro_events", "fed_announcements",
    "inflation", "interest_rates", "company_earnings", "sector_movement",
    "breaking_news", "high_risk_events", "conflicting_indicators", "noise", "edge_cases",
]

RESPONSE_SCHEMA = """{
  "flag_raised": boolean,
  "risk_score": number (0-100),
  "category": one of ["revenue","cash_flow","expenses","receivables","inventory","compliance","audit","macro","other"],
  "priority": one of ["low","medium","high","critical"],
  "reasoning": string (why this flag was or wasn't raised, grounded in the scenario given),
  "recommended_action": string (concrete next step for a finance team),
  "confidence": number (0-100)
}"""

TASK_INSTRUCTION = (
    "You are a financial risk-flagging analyst for an industrial manufacturing company. "
    "Given the scenario below, decide whether it warrants a finance flag, assess its risk, "
    "and respond with ONLY a single valid JSON object matching this exact schema — no prose, "
    "no markdown fences:\n" + RESPONSE_SCHEMA
)

COMPANIES = ["Hindalco Industries", "BHEL", "Schneider Electric", "a mid-cap steel producer",
             "a regional EPC contractor", "an aluminium smelter", "a power-transmission utility",
             "a solar EPC developer", "a busduct component supplier", "an industrial fabricator"]
SECTORS = ["power transmission", "renewable energy", "steel manufacturing", "electrical components",
           "metro rail infrastructure", "oil & gas", "cement", "semiconductor fabrication",
           "data center construction", "EV battery manufacturing"]

TEMPLATES: dict[str, list[str]] = {
    "bullish": [
        "{company} reported quarterly revenue growth of {pct}% year-on-year, driven by strong order "
        "intake in the {sector} sector. Order book stands at {value} crore with a {margin}% gross margin.",
        "{company} secured a new {value} crore contract in {sector}, expected to boost next-quarter "
        "revenue by {pct}%. Working capital position remains healthy with a current ratio of {ratio}.",
    ],
    "bearish": [
        "{company} missed quarterly revenue guidance by {pct}%, citing delays in {sector} project "
        "execution. Receivables have risen to {value} crore, with {aging}% now overdue beyond 90 days.",
        "{company}'s gross margin contracted {pct} percentage points due to rising input costs in "
        "{sector}. Short-term borrowings increased {pct2}% to fund working capital gaps.",
    ],
    "mixed_signals": [
        "{company} grew revenue {pct}% but net profit fell {pct2}% due to a one-time impairment charge "
        "in {sector}. Cash flow from operations was positive despite the profit decline.",
        "Order booking in {sector} rose {pct}% for {company}, but collections slowed, with DSO extending "
        "from {ratio} to {ratio2} days over the quarter.",
    ],
    "macro_events": [
        "A {pct}% depreciation in INR against USD is raising import costs for {sector} raw materials "
        "used by {company}, a net importer of copper and aluminium.",
        "New import duty of {pct}% on steel/aluminium announced, expected to affect {company}'s cost "
        "base in the {sector} segment starting next fiscal quarter.",
    ],
    "fed_announcements": [
        "The US Federal Reserve raised rates by {bps} bps, tightening global credit conditions. "
        "{company} has {value} crore in foreign-currency-linked term debt exposed to this move.",
        "Fed signaled a pause in rate hikes after {n} consecutive increases, easing pressure on "
        "{company}'s working capital financing costs in {sector}.",
    ],
    "inflation": [
        "Wholesale price inflation in {sector} inputs rose to {pct}%, squeezing {company}'s gross "
        "margin by an estimated {pct2} percentage points if unpassed to customers.",
        "{company} passed through a {pct}% price increase to offset input cost inflation in {sector}, "
        "with early signs of a {pct2}% dip in order volume from price-sensitive customers.",
    ],
    "interest_rates": [
        "RBI held the repo rate steady at {pct}%, keeping {company}'s CC/OD financing cost stable "
        "for the {sector} working capital cycle.",
        "A {bps} bps repo rate hike raises {company}'s annual interest burden on {value} crore "
        "of short-term borrowings by an estimated {value2} lakh.",
    ],
    "company_earnings": [
        "{company} posted EBITDA margin of {pct}%, {direction} {pct2} points from the prior quarter, "
        "with {sector} contributing the largest share of revenue.",
        "Q{q} results for {company}: net profit {direction} {pct}% YoY, revenue {value} crore, "
        "driven by {sector} order execution.",
    ],
    "sector_movement": [
        "Government capex allocation to {sector} increased {pct}% in the latest budget, expected to "
        "expand the addressable market for suppliers like {company}.",
        "{sector} sector order inflow across the industry slowed {pct}% this quarter amid project "
        "financing delays, a headwind for component suppliers.",
    ],
    "breaking_news": [
        "BREAKING: {company} announced an unplanned {pct}% capacity expansion in {sector} following "
        "a large, unannounced order win of {value} crore.",
        "BREAKING: A key {sector} customer of {company} filed for debt restructuring, putting "
        "{value} crore of receivables at risk.",
    ],
    "high_risk_events": [
        "{company} has {value} crore in receivables overdue beyond 180 days from a single {sector} "
        "customer now showing signs of financial distress.",
        "An audit flagged a {value} crore discrepancy between recorded and physically verified "
        "inventory at {company}'s {sector} production facility.",
    ],
    "conflicting_indicators": [
        "{company} shows rising revenue ({pct}%) alongside declining operating cash flow (-{pct2}%) "
        "in {sector} — order booking is strong but collections have stalled.",
        "Analysts are split on {company}: order book in {sector} grew {pct}%, but the current ratio "
        "fell from {ratio} to {ratio2}, raising liquidity questions despite top-line growth.",
    ],
    "noise": [
        "{company} updated its corporate logo and office signage across its {sector} facilities this "
        "quarter. No material financial impact was disclosed.",
        "A regional trade publication mentioned {company} in a roundup article about {sector} industry "
        "trends, without specific financial or operational detail.",
    ],
    "edge_cases": [
        "{company}'s financial statement shows revenue of {value} crore but the accompanying notes "
        "are missing entirely, and prior-period comparatives are marked 'restated' with no explanation.",
        "Data feed error: {company}'s reported current ratio is listed as {ratio} but current assets "
        "and current liabilities figures are both blank in the source document.",
    ],
}


def _fill(template: str, rng: random.Random) -> str:
    return template.format(
        company=rng.choice(COMPANIES),
        sector=rng.choice(SECTORS),
        pct=round(rng.uniform(2, 45), 1),
        pct2=round(rng.uniform(2, 30), 1),
        value=round(rng.uniform(5, 500), 1),
        value2=round(rng.uniform(5, 200), 1),
        margin=round(rng.uniform(8, 35), 1),
        ratio=round(rng.uniform(0.6, 2.5), 2),
        ratio2=round(rng.uniform(0.6, 2.5), 2),
        aging=round(rng.uniform(5, 60), 1),
        bps=rng.choice([25, 50, 75, 100]),
        n=rng.choice([2, 3, 4, 5]),
        q=rng.choice([1, 2, 3, 4]),
        direction=rng.choice(["up", "down"]),
    )


def generate(mode: str, seed: int = 42) -> list[CaseRecord]:
    """Deterministic for a given mode — same case set every call, needed for --resume
    and for fair repeated benchmark runs across models."""
    if mode not in MODE_SIZES:
        raise ValueError(f"Unknown mode {mode!r}; choose from {list(MODE_SIZES)}")
    total = MODE_SIZES[mode]
    rng = random.Random(seed)

    per_category = max(1, total // len(CATEGORIES))
    cases: list[CaseRecord] = []
    for category in CATEGORIES:
        templates = TEMPLATES[category]
        for i in range(per_category):
            template = templates[i % len(templates)]
            scenario = _fill(template, rng)
            prompt = f"{TASK_INSTRUCTION}\n\nSCENARIO:\n{scenario}"
            case_id = hashlib.sha256(f"{mode}:{category}:{i}:{scenario}".encode()).hexdigest()[:16]
            cases.append(CaseRecord(case_id=case_id, category=category, prompt=prompt))

    # Top up to hit the exact requested total (integer division leaves a remainder).
    idx = 0
    while len(cases) < total:
        category = CATEGORIES[idx % len(CATEGORIES)]
        templates = TEMPLATES[category]
        scenario = _fill(templates[idx % len(templates)], rng)
        prompt = f"{TASK_INSTRUCTION}\n\nSCENARIO:\n{scenario}"
        case_id = hashlib.sha256(f"{mode}:{category}:extra{idx}:{scenario}".encode()).hexdigest()[:16]
        cases.append(CaseRecord(case_id=case_id, category=category, prompt=prompt))
        idx += 1

    return cases
