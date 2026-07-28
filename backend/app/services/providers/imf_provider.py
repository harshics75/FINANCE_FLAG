"""IMF DataMapper API (World Economic Outlook database) — fully public, no key
required. The older IMF SDMX CompactData service is notoriously slow/unreliable for
production use, so this uses the newer, simpler DataMapper endpoint instead. Real
attempt every call; on failure this reports status="unavailable", never a guessed
number — IMF WEO values are twice-yearly estimates, so the "as_of" year may be a
forecast year, which is disclosed rather than presented as an actual.
"""
from app.services.providers.base import EconomicDataProvider
from app.services.providers.http_cache import cached_get_json

BASE_URL = "https://www.imf.org/external/datamapper/api/v1"
CACHE_TTL = 24 * 60 * 60

INDICATORS = {
    "gdp_growth_outlook": ("NGDP_RPCH", "IND", "IMF Real GDP Growth Outlook (India)", "%"),
    "inflation_outlook": ("PCPIPCH", "IND", "IMF Inflation Outlook (India)", "%"),
    "world_gdp_growth": ("NGDP_RPCH", "WEOWORLD", "IMF Real GDP Growth Outlook (World)", "%"),
}


class IMFProvider(EconomicDataProvider):
    def get_indicators(self) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for key, (indicator, country, label, unit) in INDICATORS.items():
            data = cached_get_json(
                f"market:imf:{indicator}:{country}", CACHE_TTL,
                f"{BASE_URL}/{indicator}/{country}",
            )
            result[key] = self._parse(data, indicator, country, label, unit)
        return result

    @staticmethod
    def _parse(data, indicator: str, country: str, label: str, unit: str) -> dict:
        try:
            series = data["values"][indicator][country]
            latest_year = max(series.keys())
            return {
                "name": label,
                "value": round(float(series[latest_year]), 2),
                "unit": unit,
                "as_of": latest_year,
                "is_forecast": int(latest_year) > 2025,
                "status": "live",
                "source": "IMF World Economic Outlook (DataMapper)",
            }
        except Exception:
            return {"name": label, "status": "unavailable", "source": "IMF World Economic Outlook"}
