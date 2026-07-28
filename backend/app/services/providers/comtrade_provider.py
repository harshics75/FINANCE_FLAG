"""UN Comtrade — the modern API (comtradeapi.un.org) requires a subscription key
(free tier available via the UN Comtrade portal) plus fiddly numeric commodity-code
queries (HS codes for copper=7403, aluminium=7601, electrical equipment=85xx) with a
low free-tier call quota. Given the setup cost relative to value for a v1 release,
this stays a permanent not_configured stub rather than a key-gated one — implementing
it properly means designing the HS-code query set first, not just adding a key.
"""
from app.services.providers.base import EconomicDataProvider

_STUB = {
    "status": "not_configured",
    "source": "UN Comtrade (not integrated)",
    "future_integration": "Requires a UN Comtrade subscription key + curated HS-code "
                           "query set (copper HS 7403, aluminium HS 7601, electrical "
                           "equipment HS 85xx) — comtradeapi.un.org",
}


class UNComtradeProvider(EconomicDataProvider):
    def get_indicators(self) -> dict[str, dict]:
        return {
            "copper_imports": {"name": "India Copper Imports", **_STUB},
            "aluminium_imports": {"name": "India Aluminium Imports", **_STUB},
            "electrical_equipment_trade": {"name": "Electrical Equipment Trade", **_STUB},
        }
