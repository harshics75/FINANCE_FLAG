"""Shared fetch-with-cache-and-retry helper for Market Intelligence providers. Every
provider (World Bank, IMF, Open-Meteo, GDELT, Finnhub, FRED, EIA, GNews) goes through
this so caching, retries, and failure handling behave consistently instead of being
reimplemented per provider.
"""
import json
import logging
import time

import httpx
import redis

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
_redis: redis.Redis | None = None


def _cache() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def cached_get_json(cache_key: str, ttl: int, url: str, params: dict | None = None,
                     timeout: float = 10.0, retries: int = 2):
    """Returns cached JSON if present, else fetches with retries. Returns None (never
    raises) on total failure so callers can report status="unavailable" instead of
    crashing the page or fabricating a value."""
    cache = _cache()
    cached = cache.get(cache_key)
    if cached is not None:
        return json.loads(cached)

    last_error = None
    for attempt in range(retries + 1):
        try:
            resp = httpx.get(url, params=params, timeout=timeout, follow_redirects=True)
            resp.raise_for_status()
            data = resp.json()
            cache.setex(cache_key, ttl, json.dumps(data))
            return data
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    logger.warning("cached_get_json failed for %s after %d attempt(s): %s", cache_key, retries + 1, last_error)
    return None
