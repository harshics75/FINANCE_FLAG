"""The one live provider implementation today. Thin wrapper over market_data_service
so CommodityProvider/NewsProvider consumers (routes, correlation engine, business
impact engine) don't care that Alpha Vantage happens to be behind it."""
from app.services.market_data_service import get_live_market_data, get_live_news
from app.services.providers.base import CommodityProvider, NewsProvider


class AlphaVantageCommodityProvider(CommodityProvider):
    def get_series(self, db=None) -> dict[str, dict]:
        return get_live_market_data(db=db)


class AlphaVantageNewsProvider(NewsProvider):
    def get_articles(self, topics: list[str] | None = None) -> list[dict]:
        articles = get_live_news()
        if not topics:
            return articles
        wanted = {t.lower() for t in topics}
        filtered = [a for a in articles if wanted & {t.lower() for t in a.get("topics", [])}]
        return filtered or articles
