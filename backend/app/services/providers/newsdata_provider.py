"""newsdata.io — free key required (https://newsdata.io/register). Sources real,
India-focused headlines for two Stardrive-relevant categories: metals/materials
(copper/aluminium/steel — feeds Material & Margin Intelligence) and mega-project
signals (transmission/refinery/solar park/data center/semiconductor/metro — feeds
Revenue & Opportunity Intelligence and the Executive Brief).

The free tier caps query length at 100 characters, so this is two compact `qInTitle`
queries rather than one combined one — title-only search trades recall for precision,
which matters here since a full-text search on these terms pulls in a lot of unrelated
press-release/market-research-report noise. Raw results are still noisy (celebrity
puns, archaeology finds, career-advice pieces) — see news_relevance_service.py for the
deterministic filtering/scoring layer that keeps this off the page.
"""
from app.config.settings import get_settings
from app.services.providers.base import NewsProvider
from app.services.providers.http_cache import cached_get_json

BASE_URL = "https://newsdata.io/api/1/news"
CACHE_TTL = 4 * 60 * 60
settings = get_settings()

METALS_QUERY = "copper OR aluminium OR steel OR transmission OR refinery OR substation"
PROJECTS_QUERY = '"solar park" OR "data center" OR semiconductor OR "metro rail"'


class NewsDataProvider(NewsProvider):
    def get_articles(self, topics: list[str] | None = None) -> list[dict]:
        if not settings.newsdata_api_key:
            return [{
                "status": "not_configured", "source": "newsdata.io (no API key configured)",
                "future_integration": "Set NEWSDATA_API_KEY in .env — free key at https://newsdata.io/register",
            }]
        articles = []
        for cache_key, query in (("market:newsdata:metals", METALS_QUERY),
                                  ("market:newsdata:projects", PROJECTS_QUERY)):
            data = cached_get_json(
                cache_key, CACHE_TTL, BASE_URL,
                params={"apikey": settings.newsdata_api_key, "qInTitle": query,
                        "country": "in", "language": "en"},
            )
            if not data or data.get("status") != "success":
                continue
            for a in data.get("results") or []:
                try:
                    articles.append({
                        "title": a["title"],
                        "summary": (a.get("description") or "")[:280],
                        "url": a["link"],
                        "source_name": a.get("source_name", ""),
                        "published_at": a.get("pubDate", ""),
                        "status": "live",
                        "source": "newsdata.io",
                    })
                except KeyError:
                    continue
        return articles or [{"status": "unavailable", "source": "newsdata.io"}]
