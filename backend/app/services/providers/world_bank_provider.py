"""World Bank Open Data API — fully public, no key required. Used for the macro
indicators most relevant to a manufacturer's demand outlook: GDP growth, manufacturing
value-added, exports/imports (% of GDP), and consumer-price inflation, all for India.
"""
from app.services.providers.base import EconomicDataProvider
from app.services.providers.http_cache import cached_get_json

BASE_URL = "https://api.worldbank.org/v2/country/IND/indicator"
CACHE_TTL = 24 * 60 * 60  # World Bank indicators update annually/quarterly at most

INDICATORS = {
    "gdp_growth": ("NY.GDP.MKTP.KD.ZG", "India GDP Growth", "%"),
    "manufacturing_value_added": ("NV.IND.MANF.ZS", "Manufacturing (% of GDP)", "%"),
    "exports_pct_gdp": ("NE.EXP.GNFS.ZS", "Exports (% of GDP)", "%"),
    "imports_pct_gdp": ("NE.IMP.GNFS.ZS", "Imports (% of GDP)", "%"),
    "inflation_cpi": ("FP.CPI.TOTL.ZG", "India CPI Inflation", "%"),
}


class WorldBankProvider(EconomicDataProvider):
    def get_indicators(self) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for key, (code, label, unit) in INDICATORS.items():
            data = cached_get_json(
                f"market:worldbank:{code}", CACHE_TTL,
                f"{BASE_URL}/{code}", params={"format": "json", "per_page": "1", "mrnev": "1"},
            )
            entry = self._parse(data, label, unit)
            result[key] = entry
        return result

    @staticmethod
    def _parse(data, label: str, unit: str) -> dict:
        try:
            points = data[1]
            if not points:
                raise ValueError("empty")
            point = points[0]
            return {
                "name": label,
                "value": round(float(point["value"]), 2),
                "unit": unit,
                "as_of": point["date"],
                "status": "live",
                "source": "World Bank Open Data",
            }
        except Exception:
            return {"name": label, "status": "unavailable", "source": "World Bank Open Data"}
