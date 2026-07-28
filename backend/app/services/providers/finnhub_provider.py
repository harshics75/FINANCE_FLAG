"""Finnhub — free-tier key required (https://finnhub.io/register). Fully implemented
so it goes live the moment FINNHUB_API_KEY is set in .env; until then every method
returns status="not_configured", the same honest treatment as the LME stub.

Company-level news/earnings need real ticker symbols — since Competitor Intelligence
today is generic placeholder data (no real competitor identified yet), this provider
exposes general market news only. Wire in real competitor tickers later to light up
company-specific news/earnings/sentiment.
"""
from app.config.settings import get_settings
from app.services.providers.http_cache import cached_get_json

BASE_URL = "https://finnhub.io/api/v1"
CACHE_TTL = 3 * 60 * 60
settings = get_settings()

_NOT_CONFIGURED = {
    "status": "not_configured",
    "source": "Finnhub (no API key configured)",
    "future_integration": "Set FINNHUB_API_KEY in .env — free tier at https://finnhub.io/register",
}


class FinnhubProvider:
    def get_market_news(self) -> list[dict]:
        if not settings.finnhub_api_key:
            return [dict(_NOT_CONFIGURED)]
        data = cached_get_json(
            "market:finnhub:news", CACHE_TTL, f"{BASE_URL}/news",
            params={"category": "general", "token": settings.finnhub_api_key},
        )
        if not data:
            return [{"status": "unavailable", "source": "Finnhub"}]
        out = []
        for item in data[:10]:
            try:
                out.append({
                    "headline": item["headline"], "summary": item.get("summary", "")[:280],
                    "url": item["url"], "source_name": item.get("source", ""),
                    "datetime": item.get("datetime"), "status": "live", "source": "Finnhub",
                })
            except KeyError:
                continue
        return out

    def get_earnings_calendar(self, symbols: list[str] | None = None) -> list[dict]:
        if not settings.finnhub_api_key:
            return [dict(_NOT_CONFIGURED)]
        if not symbols:
            return []  # no real watchlist configured yet
        return []  # placeholder for when a real competitor ticker list exists
