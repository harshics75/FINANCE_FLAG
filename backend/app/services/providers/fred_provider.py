"""FRED (Federal Reserve Bank of St. Louis) — free key required
(https://fred.stlouisfed.org/docs/api/api_key.html). Fully implemented so it goes
live the moment FRED_API_KEY is set; until then reports status="not_configured".

FRED's data is US-centric, but US inflation/industrial-production/rates are genuinely
relevant here since global commodity prices are USD-denominated and US industrial
demand correlates with copper/aluminum/steel pricing. Uses FRED's server-side `pc1`
transform (percent change from a year ago) so this reports rates directly instead of
computing deltas client-side.
"""
from app.config.settings import get_settings
from app.services.providers.base import EconomicDataProvider
from app.services.providers.http_cache import cached_get_json

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
CACHE_TTL = 24 * 60 * 60
settings = get_settings()

SERIES = {
    "us_cpi_inflation": ("CPIAUCSL", "pc1", "US CPI Inflation (YoY)", "%"),
    "us_industrial_production": ("INDPRO", "pc1", "US Industrial Production Growth (YoY)", "%"),
    "us_10y_treasury_yield": ("DGS10", "lin", "US 10-Year Treasury Yield", "%"),
}


class FREDProvider(EconomicDataProvider):
    def get_indicators(self) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for key, (series_id, units, label, unit) in SERIES.items():
            if not settings.fred_api_key:
                result[key] = {
                    "name": label, "status": "not_configured",
                    "source": "FRED (no API key configured)",
                    "future_integration": "Set FRED_API_KEY in .env — free key at https://fred.stlouisfed.org/docs/api/api_key.html",
                }
                continue
            data = cached_get_json(
                f"market:fred:{series_id}", CACHE_TTL, BASE_URL,
                params={
                    "series_id": series_id, "api_key": settings.fred_api_key, "file_type": "json",
                    "sort_order": "desc", "limit": 1, "units": units,
                },
            )
            result[key] = self._parse(data, label, unit)
        return result

    @staticmethod
    def _parse(data, label: str, unit: str) -> dict:
        try:
            obs = data["observations"][0]
            return {
                "name": label, "value": round(float(obs["value"]), 2), "unit": unit,
                "as_of": obs["date"], "status": "live", "source": "FRED (St. Louis Fed)",
            }
        except Exception:
            return {"name": label, "status": "unavailable", "source": "FRED"}
