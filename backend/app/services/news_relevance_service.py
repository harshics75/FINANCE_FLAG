"""Deterministic filtering and scoring for real news articles (newsdata_provider.py)
against Stardrive's actual business — no LLM involved (see relevance_scoring.py's
docstring on why scoring must stay deterministic). A free-tier title-keyword search
pulls in real signal alongside a lot of noise (archaeology finds, career-advice
pieces, market-research-report PR blasts); this module is what keeps the noise off
the page, not the search query itself.

Each article is classified as either a MATERIAL signal (bare copper/aluminium/steel
mention — commodity cost angle, materials affect every sector so this doesn't use a
sector-specific weight) or a SECTOR signal (mentions a specific project type Stardrive
sells into — scored against that sector's historical weight, same as
opportunity_extraction_service.py).
"""
import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.services import sector_profiles

RECENCY_HALF_LIFE_DAYS = 3  # news goes stale fast compared to a project pipeline

# Title substrings, checked case-insensitively, that flag an article as noise even
# though it matched the source query's keywords — observed directly from live
# newsdata.io results during development, not a hypothetical list.
DENYLIST = [
    "unearthed", "coins", "archaeology", "e-waste", "old phone",
    "market to reach", "market size", "cagr", "research report", "market research",
    "earnings call", "quarterly earnings", "jobs", "graduates", "roles among",
    "horoscope", "recipe",
    # Conflict/military — a war story mentioning "substation" or "power plant" as a
    # strike target is not a Stardrive business signal, however fresh or specific.
    "drone strike", "airstrike", "missile", "military", "war ", " war,", "conflict",
    "libya", "gaza", "ukraine war", "attack on", "torches",
    # Stock-market/IPO stories — "copper"/"aluminium" appearing in a ticker-move or
    # listing headline is a finance story about the company, not a materials signal.
    "nyse", "nasdaq", "ipo", "valuation", "stock ", "shares ", "pops ", "surges after listing",
    "jumps ", "climbs ", "rallies ", "earnings",
    # Generic CSR/PR fluff — an observance-day press release, not a business signal.
    "celebrates", "commemorates", "observes world",
]

# (sector_key, [title keywords]) — first match wins, so put more specific phrases first.
SECTOR_KEYWORDS: list[tuple[str, list[str]]] = [
    ("data_centres", ["data center", "data centre"]),
    ("semiconductor", ["semiconductor", "chip fab"]),
    ("battery_plants", ["battery plant", "gigafactory", "ev battery"]),
    ("metro_rail", ["metro rail", "metro line"]),
    ("airports", ["airport expansion", "airport terminal"]),
    ("industrial_parks", ["industrial park"]),
    ("solar", ["solar park", "solar plant", "solar power", "renewable energy"]),
    ("oil_gas", ["refinery", "petrochemical", "oil field", "gas field", "oil and gas"]),
    ("power", ["transmission line", "transmission", "substation", "power grid", "power plant"]),
    ("steel", ["steel plant", "steel mill", "steelmaker"]),
    ("water", ["water treatment", "water project"]),
    ("cement", ["cement plant"]),
]

MATERIAL_KEYWORDS = ["copper", "aluminium", "aluminum", "steel price"]
MATERIAL_WEIGHT = 0.8  # materials affect every sector's cost base, not one sector's revenue

_SECTOR_LABELS: dict[str, str] = {row[0]: row[1] for row in sector_profiles.SEED_TABLE}
_SECTOR_LABELS.update(sector_profiles.EMERGING_SECTORS)

FIGURE_RE = re.compile(r"₹\s?[\d,]+(\.\d+)?\s*(crore|cr\.?|lakh)", re.IGNORECASE)

SECTOR_POINTS = 60
RECENCY_POINTS = 25
SPECIFICITY_POINTS = 15


def _is_noise(title: str) -> bool:
    lower = title.lower()
    return any(term in lower for term in DENYLIST)


def _classify(title: str) -> tuple[str, str] | None:
    """Returns (kind, sector_key) where kind is "sector" or "material", or None if the
    title doesn't match anything we track."""
    lower = title.lower()
    for sector_key, keywords in SECTOR_KEYWORDS:
        if any(kw in lower for kw in keywords):
            return "sector", sector_key
    if any(kw in lower for kw in MATERIAL_KEYWORDS):
        return "material", ""
    return None


def _parse_pub_date(raw: str) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _recency_score(published_at: datetime | None) -> float:
    if published_at is None:
        return 0.2
    age_days = max(0.0, (datetime.now(timezone.utc) - published_at).total_seconds() / 86400)
    return 0.5 ** (age_days / RECENCY_HALF_LIFE_DAYS)


def score_and_tag_articles(db: Session, articles: list[dict]) -> list[dict]:
    """Filters out noise/unmatched articles and returns the rest tagged with sector,
    kind, relevance_score, and score_breakdown — sorted highest relevance first."""
    weights = sector_profiles.sector_weight_table(db)
    out = []
    seen_titles: set[str] = set()
    for a in articles:
        if a.get("status") != "live":
            continue
        title = a.get("title", "")
        if not title or title in seen_titles or _is_noise(title):
            continue
        classification = _classify(title)
        if classification is None:
            continue
        kind, sector_key = classification
        seen_titles.add(title)

        sector_weight = MATERIAL_WEIGHT if kind == "material" else weights.get(sector_key, 0.0)
        published_at = _parse_pub_date(a.get("published_at", ""))
        has_figure = bool(FIGURE_RE.search(title))

        sector_component = SECTOR_POINTS * max(0.0, min(1.0, sector_weight))
        recency_component = RECENCY_POINTS * _recency_score(published_at)
        specificity_component = SPECIFICITY_POINTS * (1.0 if has_figure else 0.3)
        relevance = round(sector_component + recency_component + specificity_component, 1)

        out.append({
            **a,
            "kind": kind,
            "sector": sector_key,
            "sector_label": _SECTOR_LABELS.get(sector_key, "Materials"),
            "relevance_score": max(0.0, min(100.0, relevance)),
            "score_breakdown": {
                "sector": round(sector_component, 1),
                "recency": round(recency_component, 1),
                "specificity": round(specificity_component, 1),
            },
        })
    out.sort(key=lambda a: a["relevance_score"], reverse=True)
    return out
