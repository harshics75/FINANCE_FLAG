"""Provider interfaces for Market Intelligence data.

The goal is that swapping a data source later (Alpha Vantage -> Bloomberg, a mock
infrastructure feed -> a real government API) never requires a frontend change: every
implementation returns the same shape, and every record is tagged with a `status` of
"live" (real API response), "demo" (illustrative placeholder data), "not_configured"
(interface exists, no integration wired up yet — usually missing a free API key), or
"unavailable" (integration is real and configured, but the live call failed just now,
e.g. a timeout or upstream outage — distinct from not_configured so a transient
failure never gets mistaken for "this was never wired up"). The UI renders a badge off
that field so nothing demo, unconfigured, or failed is ever presented as real.
"""
from abc import ABC, abstractmethod


class CommodityProvider(ABC):
    """A source of commodity/FX/rate quotes, keyed by series name."""

    @abstractmethod
    def get_series(self) -> dict[str, dict]:
        """Returns {series_name: {value, unit, as_of, change_pct, status, source, ...}}."""
        raise NotImplementedError


class NewsProvider(ABC):
    @abstractmethod
    def get_articles(self, topics: list[str] | None = None) -> list[dict]:
        raise NotImplementedError


class InfrastructureProvider(ABC):
    """Large capital projects (power, rail, ports, plants) relevant to industrial demand."""

    @abstractmethod
    def get_projects(self) -> list[dict]:
        raise NotImplementedError


class CompetitorProvider(ABC):
    @abstractmethod
    def get_competitors(self) -> list[dict]:
        raise NotImplementedError


class GovernmentProjectsProvider(ABC):
    """Government tenders, policy changes, duty/tariff notifications."""

    @abstractmethod
    def get_items(self) -> list[dict]:
        raise NotImplementedError


class EconomicDataProvider(ABC):
    """Macro indicators: GDP, inflation, interest rates, industrial production, trade."""

    @abstractmethod
    def get_indicators(self) -> dict[str, dict]:
        raise NotImplementedError


class WeatherProvider(ABC):
    """Logistics/supply-chain risk signals derived from weather forecasts at key hubs."""

    @abstractmethod
    def get_risk_assessment(self) -> list[dict]:
        raise NotImplementedError


class EventProvider(ABC):
    """Global event/news-event intelligence (geopolitical, supply chain, infrastructure)."""

    @abstractmethod
    def get_events(self) -> list[dict]:
        raise NotImplementedError
