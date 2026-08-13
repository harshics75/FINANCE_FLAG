from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_any
from app.database.session import get_db
from app.services import (
    business_impact_service, correlation_service, market_brief_service,
    news_relevance_service, opportunity_extraction_service,
)
from app.services.market_data_service import get_live_market_data, get_live_news
from app.services.providers.alpha_vantage_provider import AlphaVantageCommodityProvider, AlphaVantageNewsProvider
from app.services.providers.comtrade_provider import UNComtradeProvider
from app.services.providers.data_gov_in_provider import DataGovInProvider
from app.services.providers.eia_provider import EIAProvider
from app.services.providers.finnhub_provider import FinnhubProvider
from app.services.providers.frankfurter_provider import FrankfurterFXProvider
from app.services.providers.fred_provider import FREDProvider
from app.services.providers.gdelt_provider import GDELTProvider
from app.services.providers.gnews_provider import GNewsProvider
from app.services.providers.imf_provider import IMFProvider
from app.services.providers.lme_provider import LMEProvider
from app.services.providers.mock_providers import (
    MockCompetitorProvider, MockGovernmentProjectsProvider, MockInfrastructureProvider,
)
from app.services.providers.newsdata_provider import NewsDataProvider
from app.services.providers.open_meteo_provider import OpenMeteoProvider
from app.services.providers.world_bank_provider import WorldBankProvider

router = APIRouter()

_commodities = AlphaVantageCommodityProvider()
_news = AlphaVantageNewsProvider()
_lme = LMEProvider()
_fx = FrankfurterFXProvider()
_infra = MockInfrastructureProvider()
_competitors = MockCompetitorProvider()
_gov = MockGovernmentProjectsProvider()
_world_bank = WorldBankProvider()
_imf = IMFProvider()
_fred = FREDProvider()
_eia = EIAProvider()
_weather = OpenMeteoProvider()
_gdelt = GDELTProvider()
_gnews = GNewsProvider()
_finnhub = FinnhubProvider()
_comtrade = UNComtradeProvider()
_data_gov_in = DataGovInProvider()
_newsdata = NewsDataProvider()

INDUSTRIAL_TOPICS = ["manufacturing", "energy_transportation", "economy_macro"]


@router.get("/live", dependencies=[Depends(require_any)])
def live_market_data(db: Session = Depends(get_db)):
    """USD/INR, copper/aluminum/oil/brent/gas, and the Fed funds rate, cached ~24h.
    Empty dict if no API key configured. Also records today's snapshot for the
    correlation engine."""
    return get_live_market_data(db=db)


@router.get("/news", dependencies=[Depends(require_any)])
def live_news():
    """Macro/financial news with sentiment scoring, cached ~6h. Empty list if no API key configured."""
    return get_live_news()


@router.get("/commodities", dependencies=[Depends(require_any)])
def commodities(db: Session = Depends(get_db)):
    """Unified KPI-card feed: real Alpha Vantage + Frankfurter series (status=live)
    merged with LME placeholders (status=not_configured). Every entry is
    provider-tagged so the UI can badge it correctly instead of presenting a stub as
    real data."""
    live = _commodities.get_series(db=db)
    fx = _fx.get_series()
    lme = _lme.get_series()
    return {**live, **fx, **lme}


@router.get("/economic-indicators", dependencies=[Depends(require_any)])
def economic_indicators():
    """India macro (World Bank, no key), global outlook (IMF, no key), and US
    inflation/industrial-production/rates (FRED, key-gated) merged into one feed."""
    return {**_world_bank.get_indicators(), **_imf.get_indicators(), **_fred.get_indicators()}


@router.get("/energy", dependencies=[Depends(require_any)])
def energy():
    """US crude oil / natural gas inventory levels (EIA, key-gated)."""
    return _eia.get_indicators()


@router.get("/weather-risk", dependencies=[Depends(require_any)])
def weather_risk():
    """3-day logistics/supply-chain weather risk at key Indian port/hub cities (Open-Meteo, no key)."""
    return _weather.get_risk_assessment()


@router.get("/global-events", dependencies=[Depends(require_any)])
def global_events():
    """Real indexed news-event search for supply-chain/infrastructure/manufacturing signals (GDELT, no key)."""
    return _gdelt.get_events()


@router.get("/manufacturing-news", dependencies=[Depends(require_any)])
def manufacturing_news():
    """Manufacturing/infrastructure/power/renewable/data-center news (GNews, key-gated)."""
    return _gnews.get_articles()


@router.get("/company-intel", dependencies=[Depends(require_any)])
def company_intel():
    """General market news from Finnhub (key-gated). Company-specific news/earnings
    need real competitor tickers, not yet configured."""
    return _finnhub.get_market_news()


@router.get("/trade", dependencies=[Depends(require_any)])
def trade():
    """Granular commodity trade (UN Comtrade, permanent stub) + government open-data
    trade feed (data.gov.in, permanent stub) — see each provider's docstring for why
    these aren't key-gated like the others."""
    return {"comtrade": _comtrade.get_indicators(), "data_gov_in": _data_gov_in.get_items()}


@router.get("/correlations", dependencies=[Depends(require_any)])
def correlations(db: Session = Depends(get_db)):
    """Real Pearson correlation between series with enough overlapping daily history.
    Pairs without enough history report that honestly instead of a fabricated number."""
    return correlation_service.compute_correlations(db)


@router.get("/history/{series}", dependencies=[Depends(require_any)])
def series_history(series: str, db: Session = Depends(get_db)):
    """Recorded daily snapshots for one series — powers sparklines. Empty/short until
    the app has been running long enough to accumulate history; never backfilled."""
    return correlation_service.get_series_history(db, series)


@router.get("/impact", dependencies=[Depends(require_any)])
def business_impact(db: Session = Depends(get_db)):
    """Rule-based qualitative business-impact reasoning for each real commodity's
    latest move, plus any weather-flagged logistics risk. No fabricated financial
    figures — see business_impact_service."""
    market_data = get_live_market_data(db=db)
    impacts = business_impact_service.assess_all(market_data)
    impacts += business_impact_service.assess_weather(_weather.get_risk_assessment())
    return impacts


@router.get("/infrastructure", dependencies=[Depends(require_any)])
def infrastructure_projects():
    """Demo data — no infrastructure-project API is configured. See MockInfrastructureProvider."""
    return _infra.get_projects()


@router.get("/competitors", dependencies=[Depends(require_any)])
def competitors():
    """Demo data — no competitor-intelligence API is configured. See MockCompetitorProvider."""
    return _competitors.get_competitors()


@router.get("/government", dependencies=[Depends(require_any)])
def government_items():
    """Demo data — no government tender/policy API is configured. See MockGovernmentProjectsProvider."""
    return _gov.get_items()


@router.get("/industrial-news", dependencies=[Depends(require_any)])
def industrial_news():
    """Same Alpha Vantage news feed, filtered toward manufacturing/energy/macro topics
    instead of generic Wall Street headlines."""
    return _news.get_articles(topics=INDUSTRIAL_TOPICS)


@router.get("/intelligence", dependencies=[Depends(require_any)])
def market_intelligence(db: Session = Depends(get_db)):
    """The consolidated Stardrive Market & Business Intelligence page — every section
    already deterministically scored/filtered against Stardrive's historical sector
    performance before the (single, cached, non-blocking) AI Executive Brief call. See
    business_impact_service, opportunity_extraction_service, market_brief_service."""
    market_data = get_live_market_data(db=db)
    weather = _weather.get_risk_assessment()
    material_margin = business_impact_service.assess_all(market_data) + business_impact_service.assess_weather(weather)

    high_risk_hubs = [w for w in weather if w.get("risk_level") == "high"]
    macro_logistics = {
        "usd_inr": market_data.get("usd_inr"),
        "logistics_risk_hubs": high_risk_hubs,
    }

    return {
        "executive_brief": market_brief_service.get_executive_brief(db),
        "opportunities": opportunity_extraction_service.core_opportunities(db),
        "emerging_opportunities": opportunity_extraction_service.emerging_opportunities(db),
        "material_margin": material_margin,
        "core_sectors": opportunity_extraction_service.core_sector_intelligence(db),
        "market_signals": news_relevance_service.score_and_tag_articles(db, _newsdata.get_articles())[:8],
        "competitors": _competitors.get_competitors(),
        "policy_tenders": _gov.get_items(),
        "macro_logistics": macro_logistics,
    }
