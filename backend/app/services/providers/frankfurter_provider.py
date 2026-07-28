"""Frankfurter.app — ECB daily reference rates, fully free, no key. Used instead of
ExchangeRate.host, which was acquired by apilayer and now requires a paid-tier key for
most endpoints; Frankfurter covers the same EUR/CNY/GBP -> INR pairs at no cost.
USD/INR stays on Alpha Vantage since that integration already exists.
"""
from app.services.providers.base import CommodityProvider
from app.services.providers.http_cache import cached_get_json

BASE_URL = "https://api.frankfurter.dev/v1/latest"
CACHE_TTL = 24 * 60 * 60

PAIRS = {"eur_inr": "EUR", "cny_inr": "CNY", "gbp_inr": "GBP"}


class FrankfurterFXProvider(CommodityProvider):
    def get_series(self) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for key, base in PAIRS.items():
            data = cached_get_json(
                f"market:frankfurter:{base}", CACHE_TTL,
                BASE_URL, params={"from": base, "to": "INR"},
            )
            result[key] = self._parse(data, base)
        return result

    @staticmethod
    def _parse(data, base: str) -> dict:
        try:
            return {
                "pair": f"{base}/INR",
                "rate": round(float(data["rates"]["INR"]), 4),
                "as_of": data["date"],
                "status": "live",
                "source": "Frankfurter (ECB reference rates)",
            }
        except Exception:
            return {"pair": f"{base}/INR", "status": "unavailable", "source": "Frankfurter (ECB reference rates)"}
