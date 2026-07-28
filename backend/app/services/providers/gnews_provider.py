"""GNews — free key required (https://gnews.io/register). Chosen over NewsAPI.org
because GNews' free tier permits production use (NewsAPI.org's free tier is
developer/localhost-only per its ToS). Fully implemented so it goes live the moment
GNEWS_API_KEY is set; until then reports status="not_configured".
"""
from app.config.settings import get_settings
from app.services.providers.base import NewsProvider
from app.services.providers.http_cache import cached_get_json

BASE_URL = "https://gnews.io/api/v4/search"
CACHE_TTL = 3 * 60 * 60
settings = get_settings()

QUERY = "manufacturing OR infrastructure OR \"power sector\" OR \"renewable energy\" OR \"data center\" OR EPC"


class GNewsProvider(NewsProvider):
    def get_articles(self, topics: list[str] | None = None) -> list[dict]:
        if not settings.gnews_api_key:
            return [{
                "status": "not_configured", "source": "GNews (no API key configured)",
                "future_integration": "Set GNEWS_API_KEY in .env — free key at https://gnews.io/register",
            }]
        data = cached_get_json(
            "market:gnews:manufacturing", CACHE_TTL, BASE_URL,
            params={"q": QUERY, "lang": "en", "country": "in", "max": 10, "apikey": settings.gnews_api_key},
        )
        if not data or not data.get("articles"):
            return [{"status": "unavailable", "source": "GNews"}]
        out = []
        for a in data["articles"][:10]:
            try:
                out.append({
                    "title": a["title"], "summary": (a.get("description") or "")[:280],
                    "url": a["url"], "source_name": a.get("source", {}).get("name", ""),
                    "published_at": a.get("publishedAt", ""), "status": "live", "source": "GNews",
                })
            except KeyError:
                continue
        return out
