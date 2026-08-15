"""AI Executive Brief — the one place in Market Intelligence where the LLM is called.
Ranking and facts are decided entirely by deterministic code upstream (business_impact_
service.py, opportunity_extraction_service.py); the LLM's only job is to phrase the
already-selected top signals into concise brief items (see MARKET_SYSTEM_BASE).

Bounded to ONE run_json call per refresh (not one per signal), cached in-process with a
TTL, and guarded by a non-blocking lock — this app's local Ollama setup stalls badly under
concurrent LLM calls (see this session's earlier analysis-pipeline incident), so a refresh
already in flight must never be triggered twice; callers simply get the last good cache
until the in-flight refresh finishes.
"""
import logging
import threading
import time

from sqlalchemy.orm import Session

from app.agents.llm import run_json
from app.prompts import templates as T
from app.services import business_impact_service, news_relevance_service, opportunity_extraction_service
from app.services.market_data_service import get_live_market_data
from app.services.providers.newsdata_provider import NewsDataProvider

_news = NewsDataProvider()

logger = logging.getLogger(__name__)

MAX_BRIEF_ITEMS = 5
CACHE_TTL_SECONDS = 6 * 60 * 60
RISK_TONE = {"high": "red", "medium": "amber", "low": "green"}

_cache: list[dict] | None = None
_cache_expires_at: float = 0.0
_lock = threading.Lock()


def _build_signals(db: Session) -> list[dict]:
    """Deterministically selects and ranks the candidate signals — the LLM never sees
    anything that isn't already here, and never reorders this list."""
    market_data = get_live_market_data(db=db)
    impacts = business_impact_service.assess_all(market_data)
    impacts.sort(key=lambda i: {"high": 0, "medium": 1, "low": 2}.get(i["risk_level"], 3))

    news = news_relevance_service.score_and_tag_articles(db, _news.get_articles())
    opportunities = opportunity_extraction_service.core_opportunities(db)

    signals = []
    # Real, sourced news leads the brief when available — highest-quality signal.
    for n in news[:3]:
        signals.append({
            "tone": "amber" if n["kind"] == "material" else "green",
            "headline": n["title"],
            "why": f"{n['sector_label']} signal, relevance score {n['relevance_score']}/100.",
            "source": f"{n.get('source_name') or 'newsdata.io'} — {n['url']}",
        })
    for i in impacts[:2]:
        signals.append({
            "tone": RISK_TONE.get(i["risk_level"], "amber"),
            "headline": i["headline"],
            "why": i["business_impact"][0] if i["business_impact"] else "",
            "source": "Real commodity/weather data",
        })
    for o in opportunities:
        if len(signals) >= MAX_BRIEF_ITEMS:
            break
        signals.append({
            "tone": "green",
            "headline": f"{o['title']} identified in {o['location'] or o['sector_label']}",
            "why": f"{o['sector_label']} project, relevance score {o['relevance_score']}/100, stage: {o['stage']}.",
            "source": o["source_name"] or "Illustrative project pipeline (demo data)",
        })
    return signals[:MAX_BRIEF_ITEMS]


def _fallback_brief(signals: list[dict]) -> list[dict]:
    """No LLM required — used whenever the model is unavailable or returns something
    unusable, so the brief section never blocks the page."""
    return [{"tone": s["tone"], "headline": s["headline"], "why_it_matters": s["why"], "source": s["source"]}
            for s in signals]


def _generate(db: Session) -> list[dict]:
    signals = _build_signals(db)
    if not signals:
        return []

    formatted = "\n".join(
        f"{i + 1}. [{s['tone']}] {s['headline']} — {s['why']} (source: {s['source']})"
        for i, s in enumerate(signals)
    )
    try:
        parsed = run_json(T.MARKET_SYSTEM_BASE,
                          T.MARKET_EXECUTIVE_BRIEF.format(count=len(signals), signals=formatted),
                          provider="nvidia")
        items = parsed.get("brief") if isinstance(parsed, dict) else None
        if not isinstance(items, list) or not items:
            raise ValueError("LLM returned no usable brief items")
        return [
            {
                "tone": item.get("tone") or signal["tone"],
                "headline": item.get("headline") or signal["headline"],
                "why_it_matters": item.get("why_it_matters") or signal["why"],
                "source": signal["source"],
            }
            for item, signal in zip(items, signals)
        ]
    except Exception:
        logger.warning("market_brief_service: LLM brief generation failed, using templated fallback", exc_info=True)
        return _fallback_brief(signals)


def get_executive_brief(db: Session) -> list[dict]:
    global _cache, _cache_expires_at
    now = time.time()
    if _cache is not None and now < _cache_expires_at:
        return _cache

    if not _lock.acquire(blocking=False):
        return _cache or []  # a refresh is already in flight — serve stale rather than stack requests
    try:
        _cache = _generate(db)
        _cache_expires_at = time.time() + CACHE_TTL_SECONDS
        return _cache
    finally:
        _lock.release()
