"""Demo-data providers for sections that have no available public API today:
infrastructure project tracking, competitor intelligence, and government
tenders/policy. Every record is illustrative (generic names, round numbers) and
carries status="demo" plus a future_integration hint — this is UI/architecture
scaffolding, never presented as real market intelligence.

Swapping in a real feed later (a government open-data API, a manual CSV upload, an
enterprise data-lake connector) means implementing get_projects/get_competitors/
get_items against that source and returning status="live" — no frontend change.
"""
from app.services.providers.base import CompetitorProvider, GovernmentProjectsProvider, InfrastructureProvider

_DEMO = "Demo data — illustrative structure only, not a real record"


class MockInfrastructureProvider(InfrastructureProvider):
    """Illustrative project pipeline tuned to Stardrive Busducts' served markets —
    every project type here (power, metro, airport, data center, renewable,
    semiconductor, EV battery) is a segment busduct systems are actually sold into,
    so this is a realistic *shape* for the real feed even though the records
    themselves are fictional placeholders."""

    def get_projects(self) -> list[dict]:
        return [
            {
                "name": "Sample Transmission Corridor Project",
                "country": "India", "state": "Gujarat", "sector": "Power Plant / Transmission",
                "value_cr": 4200, "stage": "Tender Awarded",
                "material_demand": ["Copper", "Aluminium", "Steel"], "busduct_relevance": "high",
                "opportunity_score": 78,
                "status": "demo", "source": _DEMO,
                "future_integration": "Power Grid / Ministry of Power open data / manual upload",
            },
            {
                "name": "Sample Metro Rail Extension",
                "country": "India", "state": "Maharashtra", "sector": "Metro Rail",
                "value_cr": 9800, "stage": "Under Construction",
                "material_demand": ["Steel", "Aluminium", "Copper"], "busduct_relevance": "high",
                "opportunity_score": 65,
                "status": "demo", "source": _DEMO,
                "future_integration": "Indian Railways / NHAI open data / manual upload",
            },
            {
                "name": "Sample Solar Park Development",
                "country": "India", "state": "Rajasthan", "sector": "Renewable Energy",
                "value_cr": 2600, "stage": "Bidding Open",
                "material_demand": ["Aluminium", "Copper"], "busduct_relevance": "medium",
                "opportunity_score": 71,
                "status": "demo", "source": _DEMO,
                "future_integration": "Ministry of New and Renewable Energy / manual upload",
            },
            {
                "name": "Sample Data Center Campus",
                "country": "India", "state": "Karnataka", "sector": "Data Center",
                "value_cr": 3100, "stage": "Planning",
                "material_demand": ["Copper", "Steel"], "busduct_relevance": "high",
                "opportunity_score": 82,
                "status": "demo", "source": _DEMO,
                "future_integration": "State investment authority feed / manual upload",
            },
            {
                "name": "Sample International Airport Expansion",
                "country": "India", "state": "Telangana", "sector": "Airport",
                "value_cr": 5400, "stage": "Under Construction",
                "material_demand": ["Copper", "Aluminium"], "busduct_relevance": "medium",
                "opportunity_score": 60,
                "status": "demo", "source": _DEMO,
                "future_integration": "Airports Authority of India / manual upload",
            },
            {
                "name": "Sample Semiconductor Fab",
                "country": "India", "state": "Gujarat", "sector": "Semiconductor Plant",
                "value_cr": 22000, "stage": "Planning",
                "material_demand": ["Copper", "Steel"], "busduct_relevance": "high",
                "opportunity_score": 88,
                "status": "demo", "source": _DEMO,
                "future_integration": "Ministry of Electronics & IT / manual upload",
            },
            {
                "name": "Sample EV Battery Gigafactory",
                "country": "India", "state": "Tamil Nadu", "sector": "EV Battery Plant",
                "value_cr": 6500, "stage": "Bidding Open",
                "material_demand": ["Copper", "Aluminium"], "busduct_relevance": "high",
                "opportunity_score": 75,
                "status": "demo", "source": _DEMO,
                "future_integration": "State industries department / manual upload",
            },
            {
                "name": "Sample Industrial Park Development",
                "country": "India", "state": "Uttar Pradesh", "sector": "Industrial Park",
                "value_cr": 3800, "stage": "Tender Awarded",
                "material_demand": ["Steel", "Copper"], "busduct_relevance": "medium",
                "opportunity_score": 55,
                "status": "demo", "source": _DEMO,
                "future_integration": "State industrial development corporation / manual upload",
            },
        ]


class MockCompetitorProvider(CompetitorProvider):
    def get_competitors(self) -> list[dict]:
        return [
            {
                "name": "Competitor A", "move": "Announced capacity expansion",
                "detail": "Illustrative example of a capacity-expansion signal worth tracking.",
                "status": "demo", "source": _DEMO,
                "future_integration": "FactSet / CapitalIQ / Bloomberg / manual upload",
            },
            {
                "name": "Competitor B", "move": "Quarterly earnings released",
                "detail": "Illustrative example of an earnings-driven market-share signal.",
                "status": "demo", "source": _DEMO,
                "future_integration": "FactSet / CapitalIQ / Bloomberg / manual upload",
            },
            {
                "name": "Competitor C", "move": "New product launch",
                "detail": "Illustrative example of a product-launch competitive signal.",
                "status": "demo", "source": _DEMO,
                "future_integration": "FactSet / CapitalIQ / Bloomberg / manual upload",
            },
        ]


class MockGovernmentProjectsProvider(GovernmentProjectsProvider):
    def get_items(self) -> list[dict]:
        return [
            {
                "title": "Sample Import Duty Notification", "kind": "policy",
                "detail": "Illustrative example of a duty-change notification affecting input costs.",
                "status": "demo", "source": _DEMO,
                "future_integration": "Ministry of Commerce / CBIC open data / manual upload",
            },
            {
                "title": "Sample PLI Scheme Update", "kind": "policy",
                "detail": "Illustrative example of a production-linked-incentive policy update.",
                "status": "demo", "source": _DEMO,
                "future_integration": "Ministry of Steel / manual upload",
            },
            {
                "title": "Sample Government Tender — Transmission Equipment", "kind": "tender",
                "detail": "Illustrative example of a tender notice relevant to procurement/sales.",
                "status": "demo", "source": _DEMO,
                "future_integration": "GeM / Government Tender APIs / manual upload",
            },
        ]
