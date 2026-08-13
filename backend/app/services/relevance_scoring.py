"""Deterministic relevance scoring for external opportunities/signals — pure functions,
no I/O, no LLM. The LLM (market_brief_service.py) only ever phrases what this module has
already ranked; it never computes a score itself (see architecture notes / spec §11).

score() combines Stardrive's historical sector performance (sector_profiles.sector_weight)
with facts about a specific opportunity into one 0-100 relevance_score plus a breakdown so
the number is explainable, not a black box. Every weight is a named constant here — tune
these to change the model without touching call sites.
"""
import math
from datetime import datetime, timezone

# Component weights; must sum to 100.
SECTOR_WEIGHT_POINTS = 40
VALUE_WEIGHT_POINTS = 20
STAGE_WEIGHT_POINTS = 15
RECENCY_WEIGHT_POINTS = 10
CONFIDENCE_WEIGHT_POINTS = 10
STRATEGIC_OVERRIDE_POINTS = 5

# Log-scale ceiling for project value: a project at/above this size maxes out the value
# component. Chosen above the largest project in today's demo pipeline (~22,000 Cr) so
# there's headroom rather than everything clustering near the ceiling.
VALUE_CEILING_CR = 25_000
UNKNOWN_VALUE_SCORE = 0.3  # neutral-low, not zero — "unknown" isn't "irrelevant"

STAGE_SCORES = {
    "bidding open": 1.0,
    "tender open": 1.0,
    "tender awarded": 0.6,
    "under construction": 0.5,
    "planning": 0.4,
    "policy": 0.45,
    "tender": 0.7,
}
UNKNOWN_STAGE_SCORE = 0.35

RECENCY_HALF_LIFE_DAYS = 30  # score halves every N days since publication


def _value_score(project_value_cr: float | None) -> float:
    if project_value_cr is None or project_value_cr <= 0:
        return UNKNOWN_VALUE_SCORE
    return min(1.0, math.log10(project_value_cr + 1) / math.log10(VALUE_CEILING_CR + 1))


def _stage_score(stage: str | None, tender_deadline: datetime | None) -> float:
    base = STAGE_SCORES.get((stage or "").strip().lower(), UNKNOWN_STAGE_SCORE)
    if tender_deadline is None:
        return base
    days_left = (tender_deadline - datetime.now(timezone.utc)).days
    if 0 <= days_left <= 30:
        return max(base, 0.9)  # closing soon is urgent regardless of stage label
    return base


def _recency_score(published_at: datetime | None) -> float:
    if published_at is None:
        return 0.2  # undated — treat as stale, not as "now"
    age_days = max(0, (datetime.now(timezone.utc) - published_at).days)
    return 0.5 ** (age_days / RECENCY_HALF_LIFE_DAYS)


def score(
    *,
    sector_weight: float,
    project_value_cr: float | None = None,
    stage: str | None = None,
    tender_deadline: datetime | None = None,
    published_at: datetime | None = None,
    confidence: int = 100,
    strategic_override: bool = False,
) -> tuple[float, dict]:
    """Returns (relevance_score_0_100, breakdown). sector_weight comes from
    sector_profiles.sector_weight()/sector_weight_table() — pass the value already looked
    up for this opportunity's sector."""
    sector_component = SECTOR_WEIGHT_POINTS * max(0.0, min(1.0, sector_weight))
    value_component = VALUE_WEIGHT_POINTS * _value_score(project_value_cr)
    stage_component = STAGE_WEIGHT_POINTS * _stage_score(stage, tender_deadline)
    recency_component = RECENCY_WEIGHT_POINTS * _recency_score(published_at)
    confidence_component = CONFIDENCE_WEIGHT_POINTS * max(0.0, min(1.0, confidence / 100))
    override_component = STRATEGIC_OVERRIDE_POINTS if strategic_override else 0.0

    total = round(
        sector_component + value_component + stage_component
        + recency_component + confidence_component + override_component,
        1,
    )
    breakdown = {
        "sector": round(sector_component, 1),
        "value": round(value_component, 1),
        "stage": round(stage_component, 1),
        "recency": round(recency_component, 1),
        "confidence": round(confidence_component, 1),
        "strategic_override": override_component,
    }
    return max(0.0, min(100.0, total)), breakdown
