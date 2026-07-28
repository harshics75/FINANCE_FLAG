"""data.gov.in — India's open government data platform hosts thousands of
independently-published datasets with no unified schema; there is no single
"infrastructure projects" or "renewable energy projects" feed to query. Making this
live means finding, vetting, and hardcoding specific dataset IDs one at a time (and
each can go stale or change shape independently). That's real work worth doing
deliberately, not something to fake a generic wrapper for — so this stays a permanent
not_configured stub, same reasoning as UN Comtrade.
"""
from app.services.providers.base import GovernmentProjectsProvider

_STUB = {
    "status": "not_configured",
    "source": "data.gov.in (not integrated)",
    "future_integration": "Requires a free data.gov.in API key plus specific curated "
                           "dataset IDs (no unified schema across datasets) — "
                           "https://data.gov.in/user/register",
}


class DataGovInProvider(GovernmentProjectsProvider):
    def get_items(self) -> list[dict]:
        return [dict(_STUB, title="Government Open-Data Feed")]
