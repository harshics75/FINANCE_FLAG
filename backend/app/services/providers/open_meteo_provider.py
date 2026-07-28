"""Open-Meteo — fully free, no key, no rate limit for non-commercial-scale use. Pulls
a 3-day forecast for the hub cities most relevant to Stardrive's inbound/outbound
logistics (major ports + manufacturing/project hubs) and flags heavy rain / storm wind
/ heatwave risk with simple, disclosed thresholds — not an official IMD warning, just
a directional logistics-risk signal.
"""
from app.services.providers.base import WeatherProvider
from app.services.providers.http_cache import cached_get_json

BASE_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_TTL = 6 * 60 * 60

HUBS = {
    "mumbai": ("Mumbai (JNPT Port)", 19.076, 72.8777),
    "chennai": ("Chennai Port", 13.0827, 80.2707),
    "kolkata": ("Kolkata Port", 22.5726, 88.3639),
    "delhi_ncr": ("Delhi NCR", 28.6139, 77.2090),
    "bengaluru": ("Bengaluru", 12.9716, 77.5946),
}

HEAVY_RAIN_MM = 50
STORM_WIND_KMH = 40
HEATWAVE_C = 42


class OpenMeteoProvider(WeatherProvider):
    def get_risk_assessment(self) -> list[dict]:
        out = []
        for key, (label, lat, lon) in HUBS.items():
            data = cached_get_json(
                f"market:weather:{key}", CACHE_TTL, BASE_URL,
                params={
                    "latitude": lat, "longitude": lon,
                    "daily": "temperature_2m_max,precipitation_sum,windspeed_10m_max",
                    "timezone": "Asia/Kolkata", "forecast_days": 3,
                },
            )
            out.append(self._assess(key, label, data))
        return out

    @staticmethod
    def _assess(key: str, label: str, data) -> dict:
        try:
            daily = data["daily"]
            rain = max(daily["precipitation_sum"])
            wind = max(daily["windspeed_10m_max"])
            temp = max(daily["temperature_2m_max"])
            flags = []
            if rain >= HEAVY_RAIN_MM:
                flags.append("heavy_rain")
            if wind >= STORM_WIND_KMH:
                flags.append("storm_wind")
            if temp >= HEATWAVE_C:
                flags.append("heatwave")
            risk = "high" if flags else "low"
            return {
                "hub": label, "key": key,
                "max_rain_mm_3d": round(rain, 1), "max_wind_kmh_3d": round(wind, 1), "max_temp_c_3d": round(temp, 1),
                "flags": flags, "risk_level": risk,
                "status": "live", "source": "Open-Meteo (3-day forecast)",
            }
        except Exception:
            return {"hub": label, "key": key, "status": "unavailable", "source": "Open-Meteo"}
