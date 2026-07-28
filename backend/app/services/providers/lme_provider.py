"""LME data requires a paid licensed feed (LME Data API, Refinitiv, or a Bloomberg
Terminal entitlement) — none of which are configured in this deployment. Rather than
omit the London Metal Exchange section entirely, this provider returns an explicit
`not_configured` stub per series so the frontend can render the card with a clear
"Future Enterprise Integration" badge instead of silently hiding the capability.

Wiring in a real feed later means implementing these same methods against the vendor
SDK/API — no caller-side changes required.
"""
from app.services.providers.base import CommodityProvider

LME_SERIES = ["lme_copper", "lme_aluminium", "lme_nickel", "lme_zinc", "lme_lead", "lme_tin", "lme_steel"]
LME_LABELS = {
    "lme_copper": "LME Copper", "lme_aluminium": "LME Aluminium", "lme_nickel": "LME Nickel",
    "lme_zinc": "LME Zinc", "lme_lead": "LME Lead", "lme_tin": "LME Tin", "lme_steel": "LME Steel",
}


def _stub(label: str) -> dict:
    return {
        "name": label,
        "status": "not_configured",
        "source": "LME Data API (not configured)",
        "future_integration": "Bloomberg Terminal / LME Data API / Refinitiv Eikon",
    }


class LMEProvider(CommodityProvider):
    def get_series(self) -> dict[str, dict]:
        return {key: _stub(LME_LABELS[key]) for key in LME_SERIES}

    def get_copper(self) -> dict:
        return _stub(LME_LABELS["lme_copper"])

    def get_aluminium(self) -> dict:
        return _stub(LME_LABELS["lme_aluminium"])

    def get_nickel(self) -> dict:
        return _stub(LME_LABELS["lme_nickel"])

    def get_inventory(self) -> dict:
        return {
            "name": "LME Warehouse Inventory",
            "status": "not_configured",
            "source": "LME Data API (not configured)",
            "future_integration": "LME Data API",
        }
