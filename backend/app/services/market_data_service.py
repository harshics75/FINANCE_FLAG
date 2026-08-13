"""Live market data from Alpha Vantage — USD/INR, copper/aluminum/oil, the Fed funds
rate, and macro news with sentiment — cached in Redis for a day since the free tier
allows only 25 requests/day. Used to ground the market_comparison agent in real
numbers instead of the LLM's static training-data guesses, and exposed directly to
the frontend via GET /market/live and GET /market/news.

Note: no free, reliable API for the RBI repo rate was found, so it's omitted rather
than guessed at.
"""
import json
import logging
import threading
import time
from datetime import datetime, timezone

import httpx
import redis

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
_USE_REDIS = settings.redis_url.startswith(("redis://", "rediss://", "unix://"))

# In-process fallback for local dev (REDIS_URL=memory://), matching the pattern
# used by progress_service.py and providers/http_cache.py.
_memory_store: dict[str, tuple[float, str]] = {}
_memory_lock = threading.Lock()

BASE_URL = "https://www.alphavantage.co/query"
CACHE_TTL_SECONDS = 24 * 60 * 60
NEWS_CACHE_TTL_SECONDS = 6 * 60 * 60  # news moves faster than monthly commodity data
SERIES = {
    "copper": ("COPPER", "Copper (global avg)"),
    "aluminum": ("ALUMINUM", "Aluminum (global avg)"),
    "oil": ("WTI", "Crude Oil (WTI)"),
    "brent": ("BRENT", "Crude Oil (Brent)"),
    "natural_gas": ("NATURAL_GAS", "Natural Gas"),
    "fed_funds_rate": ("FEDERAL_FUNDS_RATE", "US Fed Funds Rate"),
}

_redis: redis.Redis | None = None


class _MemoryCache:
    """Drop-in stand-in for the subset of the redis-py interface used here."""

    def get(self, key: str) -> str | None:
        with _memory_lock:
            entry = _memory_store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if time.time() >= expires_at:
                del _memory_store[key]
                return None
            return value

    def setex(self, key: str, ttl: int, value: str) -> None:
        with _memory_lock:
            _memory_store[key] = (time.time() + ttl, value)


_memory_cache = _MemoryCache()


def _cache():
    global _redis
    if not _USE_REDIS:
        return _memory_cache
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def _get_json(params: dict) -> dict | None:
    try:
        resp = httpx.get(BASE_URL, params={**params, "apikey": settings.alpha_vantage_api_key}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "Information" in data or "Note" in data or "Error Message" in data:
            logger.warning("Alpha Vantage API issue: %s", data)
            return None
        return data
    except Exception:
        logger.exception("Alpha Vantage request failed: %s", params)
        return None


def _fetch_usd_inr() -> dict | None:
    data = _get_json({"function": "CURRENCY_EXCHANGE_RATE", "from_currency": "USD", "to_currency": "INR"})
    if not data:
        return None
    rate = data.get("Realtime Currency Exchange Rate", {})
    try:
        return {
            "pair": "USD/INR",
            "rate": round(float(rate["5. Exchange Rate"]), 4),
            "last_refreshed": rate.get("6. Last Refreshed", ""),
            "status": "live",
            "source": "Alpha Vantage",
        }
    except (KeyError, ValueError):
        return None


def _fetch_series(name: str, function: str) -> dict | None:
    """Generic fetcher for Alpha Vantage's {name, unit, data:[{date,value}]} shape,
    shared by commodities and economic indicators alike."""
    data = _get_json({"function": function, "interval": "monthly"})
    if not data or not data.get("data"):
        return None
    points = data["data"]
    try:
        latest = float(points[0]["value"])
        prior = float(points[1]["value"]) if len(points) > 1 else None
        change_pct = round((latest - prior) / prior * 100, 2) if prior else None
        return {
            "name": name,
            "unit": data.get("unit", ""),
            "value": round(latest, 2),
            "as_of": points[0]["date"],
            "month_change_pct": change_pct,
            "status": "live",
            "source": "Alpha Vantage",
        }
    except (KeyError, ValueError, IndexError, ZeroDivisionError):
        return None


def _fetch_news() -> list[dict] | None:
    data = _get_json({"function": "NEWS_SENTIMENT", "limit": "8"})
    if not data or not data.get("feed"):
        return None
    articles = []
    for item in data["feed"][:8]:
        try:
            articles.append({
                "title": item["title"],
                "url": item["url"],
                "source": item.get("source", ""),
                "time_published": item.get("time_published", ""),
                "summary": item.get("summary", "")[:280],
                "sentiment_score": float(item.get("overall_sentiment_score", 0)),
                "sentiment_label": item.get("overall_sentiment_label", "Neutral"),
                "topics": [t["topic"] for t in item.get("topics", [])[:3]],
            })
        except (KeyError, ValueError):
            continue
    return articles or None


def _cached_or_fetch(cache, cache_key: str, ttl: int, fetch_fn, made_live_call: bool) -> tuple:
    cached = cache.get(cache_key)
    if cached is not None:
        return json.loads(cached), made_live_call
    if made_live_call:
        time.sleep(1.1)  # stay under Alpha Vantage's 1 req/sec burst limit
    fetched = fetch_fn()
    if fetched:
        cache.setex(cache_key, ttl, json.dumps(fetched))
    return fetched, True


def get_live_market_data(db=None) -> dict:
    """Returns cached (or freshly fetched) USD/INR, copper/aluminum/oil/brent/gas, and
    the Fed funds rate. Any entry the API key can't produce is simply omitted, not
    fabricated. When a `db` session is passed, each series' latest value is recorded
    into MarketSnapshot (deduped per day) so the correlation engine has real history
    to grow into instead of being backfilled with guesses."""
    if not settings.alpha_vantage_api_key:
        return {}

    cache = _cache()
    result: dict = {}
    made_live_call = False

    value, made_live_call = _cached_or_fetch(cache, "market:usd_inr", CACHE_TTL_SECONDS, _fetch_usd_inr, made_live_call)
    if value:
        result["usd_inr"] = value

    for key, (function, _) in SERIES.items():
        value, made_live_call = _cached_or_fetch(
            cache, f"market:{key}", CACHE_TTL_SECONDS, lambda k=key, f=function: _fetch_series(k, f), made_live_call)
        if value:
            result[key] = value

    if db is not None:
        _record_snapshots(db, result)

    return result


def _record_snapshots(db, result: dict) -> None:
    from app.models.models import MarketSnapshot

    day_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    for series, payload in result.items():
        value = payload.get("rate") if series == "usd_inr" else payload.get("value")
        if value is None:
            continue
        exists = (
            db.query(MarketSnapshot.id)
            .filter(MarketSnapshot.series == series)
            .filter(MarketSnapshot.recorded_at >= day_start)
            .first()
        )
        if exists:
            continue
        db.add(MarketSnapshot(series=series, value=float(value), source="alpha_vantage"))
    db.commit()


def get_live_news() -> list[dict]:
    """Returns cached (or freshly fetched) macro/financial news with sentiment."""
    if not settings.alpha_vantage_api_key:
        return []

    cache = _cache()
    cached = cache.get("market:news")
    if cached is not None:
        return json.loads(cached)

    articles = _fetch_news()
    if articles:
        cache.setex("market:news", NEWS_CACHE_TTL_SECONDS, json.dumps(articles))
    return articles or []
