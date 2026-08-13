"""Shared fetch-with-cache-and-retry helper for Market Intelligence providers. Every
provider (World Bank, IMF, Open-Meteo, GDELT, Finnhub, FRED, EIA, GNews) goes through
this so caching, retries, and failure handling behave consistently instead of being
reimplemented per provider.
"""
import json
import logging
import threading
import time

import httpx
import redis

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
_redis: redis.Redis | None = None
_USE_REDIS = settings.redis_url.startswith(("redis://", "rediss://", "unix://"))

# In-process fallback for local dev (REDIS_URL=memory://), matching the pattern
# used by progress_service.py. Entries are (expires_at, value); expiry is checked
# lazily on read rather than via a background sweep.
_memory_store: dict[str, tuple[float, str]] = {}
_memory_lock = threading.Lock()


def _cache() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def _cache_get(key: str) -> str | None:
    if _USE_REDIS:
        return _cache().get(key)
    with _memory_lock:
        entry = _memory_store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.time() >= expires_at:
            del _memory_store[key]
            return None
        return value


def _cache_setex(key: str, ttl: int, value: str) -> None:
    if _USE_REDIS:
        _cache().setex(key, ttl, value)
    else:
        with _memory_lock:
            _memory_store[key] = (time.time() + ttl, value)


def cached_get_json(cache_key: str, ttl: int, url: str, params: dict | None = None,
                     timeout: float = 10.0, retries: int = 2):
    """Returns cached JSON if present, else fetches with retries. Returns None (never
    raises) on total failure so callers can report status="unavailable" instead of
    crashing the page or fabricating a value."""
    cached = _cache_get(cache_key)
    if cached is not None:
        return json.loads(cached)

    last_error = None
    for attempt in range(retries + 1):
        try:
            resp = httpx.get(url, params=params, timeout=timeout, follow_redirects=True)
            resp.raise_for_status()
            data = resp.json()
            _cache_setex(cache_key, ttl, json.dumps(data))
            return data
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    logger.warning("cached_get_json failed for %s after %d attempt(s): %s", cache_key, retries + 1, last_error)
    return None
