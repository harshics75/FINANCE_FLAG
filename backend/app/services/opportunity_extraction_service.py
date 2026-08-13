"""Step 1 of the opportunity pipeline (see architecture plan): scores the existing demo
infrastructure-project records through relevance_scoring.py, using Stardrive's real
historical sector performance, instead of their old hand-picked opportunity_score. Step 2
(real GDELT/GNews-sourced live opportunities, replacing/augmenting these where a real
signal exists) is a flagged follow-up, not built here — see plan's "explicitly out of
scope" section for why it ships separately.
"""
from sqlalchemy.orm import Session

from app.services import relevance_scoring, sector_profiles
from app.services.providers.mock_providers import MockInfrastructureProvider

_infra = MockInfrastructureProvider()

# Maps each mock project's free-text `sector` label to a canonical sector key + whether
# it's a core Stardrive market (has historical exposure) or an emerging opportunity that
# should be labelled as such rather than implied to be an established market.
SECTOR_MAP: dict[str, tuple[str, bool]] = {
    "Power Plant / Transmission": ("power", False),
    "Metro Rail": ("metro_rail", True),
    "Renewable Energy": ("solar", False),
    "Data Center": ("data_centres", True),
    "Airport": ("airports", True),
    "Semiconductor Plant": ("semiconductor", True),
    "EV Battery Plant": ("battery_plants", True),
    "Industrial Park": ("industrial_parks", True),
}

# Demo records carry no real confidence signal from an extraction model; 70 reflects
# "structurally plausible illustrative data", well below the 100 a verified live record
# or a manually-curated entry would carry.
DEMO_CONFIDENCE = 70


def get_scored_opportunities(db: Session) -> list[dict]:
    """Infrastructure project demo records scored via relevance_scoring.py, sorted by
    relevance_score descending. Every record keeps status="demo" — nothing here claims to
    be live data (see mock_providers.py docstring)."""
    weights = sector_profiles.sector_weight_table(db)
    out = []
    for project in _infra.get_projects():
        sector_key, is_emerging = SECTOR_MAP.get(project["sector"], ("mining_infra_others", True))
        sw = weights.get(sector_key, sector_profiles.EMERGING_BASELINE_WEIGHT)
        relevance, breakdown = relevance_scoring.score(
            sector_weight=sw,
            project_value_cr=project.get("value_cr"),
            stage=project.get("stage"),
            confidence=DEMO_CONFIDENCE,
        )
        out.append({
            "title": project["name"],
            "sector": sector_key,
            "sector_label": project["sector"],
            "is_emerging": is_emerging,
            "location": ", ".join(p for p in (project.get("state"), project.get("country")) if p),
            "project_value_cr": project.get("value_cr"),
            "stardrive_opportunity_value_cr": None,
            "stage": project.get("stage", ""),
            "material_demand": project.get("material_demand", []),
            "busduct_relevance": project.get("busduct_relevance", "low"),
            "relevance_score": relevance,
            "score_breakdown": breakdown,
            "confidence": DEMO_CONFIDENCE,
            "source_name": project.get("source", ""),
            "status": project.get("status", "demo"),
            "future_integration": project.get("future_integration", ""),
        })
    out.sort(key=lambda o: o["relevance_score"], reverse=True)
    return out


def core_opportunities(db: Session) -> list[dict]:
    return [o for o in get_scored_opportunities(db) if not o["is_emerging"]]


def emerging_opportunities(db: Session) -> list[dict]:
    return [o for o in get_scored_opportunities(db) if o["is_emerging"]]


def _relevance_label(weight: float) -> str:
    if weight >= 0.75:
        return "very high"
    if weight >= 0.5:
        return "high"
    if weight >= 0.25:
        return "medium"
    return "low"


def core_sector_intelligence(db: Session) -> list[dict]:
    """Compact per-sector rollup for §4 Core Sector Intelligence — deterministic, no
    LLM: historical performance from sector_profiles, live counts from today's scored
    opportunities."""
    weights = sector_profiles.sector_weight_table(db)
    opportunities = core_opportunities(db)
    out = []
    for p in sector_profiles.list_sector_profiles(db, dimension="sector"):
        sector_opps = [o for o in opportunities if o["sector"] == p.key]
        value_sum = sum(o["project_value_cr"] for o in sector_opps if o["project_value_cr"])
        out.append({
            "sector": p.key,
            "label": p.label,
            "tier": p.tier,
            "stardrive_relevance": _relevance_label(weights.get(p.key, 0)),
            "relevant_opportunities": len(sector_opps),
            "potential_project_value_cr": value_sum or None,
            "historical_enquiry_cr": p.enquiry_cr,
            "historical_orders_cr": p.orders_cr,
            "historical_conversion_pct": p.conversion_pct,
        })
    return sorted(out, key=lambda s: s["tier"])
