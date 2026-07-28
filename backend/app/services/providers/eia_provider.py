"""US EIA (Energy Information Administration) — free key required
(https://www.eia.gov/opendata/register.php). Fully implemented so it goes live the
moment EIA_API_KEY is set; until then reports status="not_configured". Uses EIA v2's
`seriesid` convenience route (legacy v1-style series IDs) rather than the newer
facets/data query shape, since it's a single simple GET per series.
"""
from app.config.settings import get_settings
from app.services.providers.base import EconomicDataProvider
from app.services.providers.http_cache import cached_get_json

BASE_URL = "https://api.eia.gov/v2/seriesid"
CACHE_TTL = 24 * 60 * 60
settings = get_settings()

SERIES = {
    "us_crude_oil_stocks": ("PET.WCESTUS1.W", "US Crude Oil Ending Stocks (weekly)", "thousand barrels"),
    "us_natural_gas_storage": ("NG.NW2_EPG0_SWO_R48_BCF.W", "US Natural Gas Storage — Lower 48 (weekly)", "Bcf"),
}


class EIAProvider(EconomicDataProvider):
    def get_indicators(self) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for key, (series_id, label, unit) in SERIES.items():
            if not settings.eia_api_key:
                result[key] = {
                    "name": label, "status": "not_configured",
                    "source": "EIA (no API key configured)",
                    "future_integration": "Set EIA_API_KEY in .env — free key at https://www.eia.gov/opendata/register.php",
                }
                continue
            data = cached_get_json(
                f"market:eia:{series_id}", CACHE_TTL, f"{BASE_URL}/{series_id}",
                params={"api_key": settings.eia_api_key},
            )
            result[key] = self._parse(data, label, unit)
        return result

    @staticmethod
    def _parse(data, label: str, unit: str) -> dict:
        try:
            point = data["response"]["data"][0]
            return {
                "name": label, "value": round(float(point["value"]), 1), "unit": unit,
                "as_of": point["period"], "status": "live", "source": "EIA",
            }
        except Exception:
            return {"name": label, "status": "unavailable", "source": "EIA"}
