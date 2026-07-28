import {
  AlertTriangle, Cloud, CloudRain, ExternalLink, Factory, Fuel, Globe2, Newspaper, Sparkles, Thermometer, Wind,
} from "lucide-react";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import { SectionHeader } from "../components/ui/InsightCard";
import CommodityCard from "../components/ui/CommodityCard";
import EconomicIndicatorCard from "../components/ui/EconomicIndicatorCard";
import StatusBadge from "../components/ui/StatusBadge";
import {
  useBusinessImpact, useCommodities, useEconomicIndicators, useEnergyIndicators, useGlobalEvents,
  useIndustrialNews, useManufacturingNews, useWeatherRisk,
} from "../hooks/useDashboard";

const TONES: Record<string, string> = {
  usd_inr: "#33D6FF", eur_inr: "#7B78FF", cny_inr: "#FF7A93", gbp_inr: "#FFB347",
  copper: "#FFB347", aluminum: "#8B94B5", oil: "#7B78FF", natural_gas: "#3EE6A8",
  lme_copper: "#FFB347", lme_aluminium: "#8B94B5",
};

const LABELS: Record<string, string> = {
  usd_inr: "USD / INR", eur_inr: "EUR / INR", cny_inr: "CNY / INR", gbp_inr: "GBP / INR",
  copper: "Copper (Global Avg)", aluminum: "Aluminum (Global Avg)",
  oil: "Crude Oil (WTI)", natural_gas: "Natural Gas", lme_copper: "LME Copper", lme_aluminium: "LME Aluminium",
};

const COMMODITY_KEYS = ["copper", "aluminum", "oil", "natural_gas", "lme_copper", "lme_aluminium"];
const CURRENCY_KEYS = ["usd_inr", "eur_inr", "cny_inr", "gbp_inr"];
const ECONOMIC_KEYS = ["inflation_cpi", "gdp_growth", "manufacturing_value_added", "us_cpi_inflation", "us_industrial_production", "us_10y_treasury_yield"];

const RISK_TONE: Record<string, string> = {
  low: "text-up border-up/30 bg-up/10", medium: "text-amber border-amber/30 bg-amber/10", high: "text-down border-down/30 bg-down/10",
};

const FLAG_ICON: Record<string, any> = { heavy_rain: CloudRain, storm_wind: Wind, heatwave: Thermometer };
const FLAG_LABEL: Record<string, string> = { heavy_rain: "Heavy Rain", storm_wind: "Storm Wind", heatwave: "Heatwave" };

export default function MarketIntelligenceOperations() {
  const { data: commodities, isLoading } = useCommodities();
  const { data: impacts } = useBusinessImpact();
  const { data: econ } = useEconomicIndicators();
  const { data: energy } = useEnergyIndicators();
  const { data: weather } = useWeatherRisk();
  const { data: events } = useGlobalEvents();
  const { data: mfgNews } = useManufacturingNews();
  const { data: industrialNews, isLoading: loadingNews } = useIndustrialNews();

  if (isLoading) return <DashboardSkeleton />;

  const hasLive = commodities && Object.values(commodities).some((c) => c.status === "live");
  const highRiskHubs = (weather ?? []).filter((w) => w.risk_level === "high");
  const gnewsConfigured = mfgNews && mfgNews[0]?.status !== "not_configured";

  return (
    <div className="space-y-6 animate-rise">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Market Intelligence — Operations</h1>
        <p className="text-sm text-mute mt-1">For Procurement, Manufacturing, Finance &amp; Operations — what changed, and what to do today.</p>
      </div>

      {/* Executive Summary / Daily AI Business Impact */}
      <div className="panel p-5">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="w-8 h-8 rounded-lg bg-grad grid place-items-center shrink-0 shadow-[0_0_16px_rgba(93,140,255,.4)]">
            <Sparkles size={16} className="text-ink" />
          </div>
          <span className="text-sm font-semibold">Daily AI Business Impact</span>
        </div>
        {!hasLive ? (
          <p className="text-sm text-mute">Live market data unavailable — configure ALPHA_VANTAGE_API_KEY to enable this page.</p>
        ) : impacts && impacts.length > 0 ? (
          <div className="space-y-2">
            {impacts.map((i) => (
              <div key={i.series} className="flex items-start gap-2.5 text-sm">
                <span className={`text-[9px] font-mono uppercase border rounded px-1.5 py-0.5 mt-0.5 shrink-0 ${RISK_TONE[i.risk_level]}`}>{i.risk_level}</span>
                <span className="text-slate-300">{i.headline} — {i.business_impact[0]}</span>
              </div>
            ))}
            <p className="text-[10px] text-faint pt-2">Rule-based qualitative reasoning from real commodity moves and weather forecasts — not fabricated financial figures.</p>
          </div>
        ) : (
          <p className="text-sm text-mute">No material moves or logistics risks to report today.</p>
        )}
      </div>

      {/* Commodity Intelligence */}
      <div>
        <SectionHeader title="Commodity Intelligence" icon={Factory} tone="#FFB347" />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {COMMODITY_KEYS.map((key) => commodities?.[key] && (
            <CommodityCard key={key} seriesKey={key} label={LABELS[key] ?? key}
              data={commodities[key]} impact={(impacts ?? []).find((i) => i.series === key)} tone={TONES[key] ?? "#33D6FF"} />
          ))}
        </div>
      </div>

      {/* Currency Intelligence */}
      <div>
        <SectionHeader title="Currency Intelligence" icon={Globe2} tone="#33D6FF" />
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {CURRENCY_KEYS.map((key) => commodities?.[key] && (
            <CommodityCard key={key} seriesKey={key} label={LABELS[key] ?? key} data={commodities[key]} tone={TONES[key] ?? "#33D6FF"} />
          ))}
        </div>
      </div>

      {/* Economic Indicators + Energy Intelligence */}
      <div className="grid lg:grid-cols-2 gap-4">
        <div>
          <SectionHeader title="Economic Indicators" icon={Sparkles} tone="#7B78FF" />
          <div className="grid sm:grid-cols-2 gap-3">
            {ECONOMIC_KEYS.map((key) => econ?.[key] && (
              <EconomicIndicatorCard key={key} data={econ[key]} tone="#7B78FF" />
            ))}
          </div>
        </div>
        <div>
          <SectionHeader title="Energy Intelligence" icon={Fuel} tone="#FF7A93" />
          <div className="grid sm:grid-cols-2 gap-3">
            {energy && Object.values(energy).map((e, i) => <EconomicIndicatorCard key={i} data={e} tone="#FF7A93" />)}
          </div>
        </div>
      </div>

      {/* Weather Intelligence / Shipping & Logistics Risk */}
      <div>
        <SectionHeader title="Weather & Shipping/Logistics Risk" icon={Cloud} tone="#33D6FF" />
        {highRiskHubs.length > 0 && (
          <div className="panel p-3 mb-3 border border-down/25 bg-down/5 flex items-start gap-2.5">
            <AlertTriangle size={15} className="text-down mt-0.5 shrink-0" />
            <p className="text-sm text-slate-300">
              <span className="text-down font-semibold">{highRiskHubs.length} logistics hub{highRiskHubs.length > 1 ? "s" : ""} at risk</span> in the next 3 days — review inbound/outbound shipping schedules.
            </p>
          </div>
        )}
        <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {(weather ?? []).map((w) => (
            <div key={w.key} className="panel p-3.5">
              <div className="flex items-start justify-between gap-2">
                <span className="text-xs font-medium">{w.hub}</span>
                <StatusBadge status={w.status} />
              </div>
              {w.status === "live" ? (
                <>
                  <div className="flex gap-2 mt-2 text-[10px] text-mute">
                    <span>{w.max_rain_mm_3d}mm rain</span> · <span>{w.max_wind_kmh_3d}km/h wind</span> · <span>{w.max_temp_c_3d}°C</span>
                  </div>
                  {w.flags && w.flags.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {w.flags.map((f) => {
                        const Icon = FLAG_ICON[f];
                        return (
                          <span key={f} className="flex items-center gap-1 text-[9px] uppercase font-mono text-down border border-down/30 bg-down/10 rounded px-1.5 py-0.5">
                            {Icon && <Icon size={9} />} {FLAG_LABEL[f]}
                          </span>
                        );
                      })}
                    </div>
                  ) : <p className="text-[10px] text-up mt-2">No weather risk flagged</p>}
                </>
              ) : <p className="text-[10px] text-faint mt-2">Forecast unavailable</p>}
            </div>
          ))}
        </div>
      </div>

      {/* Manufacturing / Power Sector / Global Event News */}
      <div className="grid lg:grid-cols-2 gap-4">
        <div>
          <SectionHeader title="Manufacturing & Industrial News" icon={Newspaper} tone="#3EE6A8" />
          <div className="panel p-4">
            {!gnewsConfigured ? (
              <div className="flex items-center justify-between">
                <p className="text-sm text-mute">Configure GNEWS_API_KEY for curated manufacturing/power/renewable news.</p>
                <StatusBadge status="not_configured" />
              </div>
            ) : (
              <ul className="space-y-3">
                {(mfgNews ?? []).map((a, i) => (
                  <li key={i} className="border-b border-panelEdge last:border-0 pb-3 last:pb-0">
                    <a href={a.url} target="_blank" rel="noreferrer" className="flex items-start justify-between gap-3 group">
                      <span className="text-sm font-medium group-hover:text-amber transition-colors">{a.title}</span>
                      <ExternalLink size={13} className="text-mute shrink-0 mt-0.5" />
                    </a>
                    <p className="text-xs text-mute mt-1 line-clamp-2">{a.summary}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        <div>
          <SectionHeader title="Global Event Intelligence" icon={Globe2} tone="#7B78FF" />
          <div className="panel p-4">
            {!events || events.length === 0 ? (
              <p className="text-sm text-mute">No events matched right now.</p>
            ) : (
              <ul className="space-y-3">
                {events.map((e, i) => (
                  <li key={i} className="border-b border-panelEdge last:border-0 pb-3 last:pb-0">
                    <a href={e.url} target="_blank" rel="noreferrer" className="flex items-start justify-between gap-3 group">
                      <span className="text-sm font-medium group-hover:text-cyan transition-colors">{e.title}</span>
                      <ExternalLink size={13} className="text-mute shrink-0 mt-0.5" />
                    </a>
                    <p className="text-[10px] text-mute mt-1">{e.domain} · {e.source_country}</p>
                  </li>
                ))}
              </ul>
            )}
            <p className="text-[10px] text-faint pt-3">Real indexed news-event search via GDELT — no API key required.</p>
          </div>
        </div>
      </div>

      <div>
        <SectionHeader title="Industrial & Macro News" icon={Newspaper} tone="#33D6FF" />
        <div className="panel p-4">
          {loadingNews ? (
            <p className="text-sm text-mute">Loading…</p>
          ) : !industrialNews || industrialNews.length === 0 ? (
            <p className="text-sm text-mute">No news available — configure ALPHA_VANTAGE_API_KEY to enable this feed.</p>
          ) : (
            <ul className="space-y-3">
              {industrialNews.map((a: any, i: number) => (
                <li key={i} className="border-b border-panelEdge last:border-0 pb-3 last:pb-0">
                  <a href={a.url} target="_blank" rel="noreferrer" className="flex items-start justify-between gap-3 group">
                    <span className="text-sm font-medium group-hover:text-amber transition-colors">{a.title}</span>
                    <ExternalLink size={13} className="text-mute shrink-0 mt-0.5" />
                  </a>
                  <p className="text-xs text-mute mt-1 line-clamp-2">{a.summary}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
