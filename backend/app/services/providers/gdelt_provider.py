"""GDELT DOC 2.0 API — fully free, no key, no signup. Global news-event search used
for geopolitical/supply-chain/infrastructure signals relevant to India's industrial
sector — the "global event intelligence" layer, sourced from real indexed news
articles rather than a curated feed.
"""
from app.services.providers.base import EventProvider
from app.services.providers.http_cache import cached_get_json

BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
CACHE_TTL = 3 * 60 * 60

QUERY = '("supply chain" OR infrastructure OR manufacturing OR "power sector" OR "renewable energy") India'


class GDELTProvider(EventProvider):
    def get_events(self) -> list[dict]:
        data = cached_get_json(
            "market:gdelt:events", CACHE_TTL, BASE_URL,
            params={"query": QUERY, "mode": "artlist", "maxrecords": 10, "format": "json", "sort": "hybridrel"},
            timeout=6.0, retries=1,  # GDELT is public but rate-limited/occasionally slow; fail fast, rely on cache
        )
        if not data or not data.get("articles"):
            return []
        out = []
        for a in data["articles"][:10]:
            try:
                out.append({
                    "title": a["title"],
                    "url": a["url"],
                    "domain": a.get("domain", ""),
                    "source_country": a.get("sourcecountry", ""),
                    "seen_date": a.get("seendate", ""),
                    "status": "live",
                    "source": "GDELT",
                })
            except KeyError:
                continue
        return out
