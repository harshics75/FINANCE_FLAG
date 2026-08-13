import {
  AlertTriangle, Cloud, Factory, Gavel, Map, Newspaper, Sparkles, Swords, Target, TrendingUp,
} from "lucide-react";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import { SectionHeader } from "../components/ui/InsightCard";
import ExecutiveBriefItem from "../components/ui/ExecutiveBriefItem";
import OpportunityCard from "../components/ui/OpportunityCard";
import SectorIntelCard from "../components/ui/SectorIntelCard";
import MarketSignalItem from "../components/ui/MarketSignalItem";
import CommodityCard from "../components/ui/CommodityCard";
import StatusBadge from "../components/ui/StatusBadge";
import { useCommodities, useMarketIntelligence } from "../hooks/useDashboard";

const RISK_TONE: Record<string, string> = {
  low: "text-up border-up/30 bg-up/10", medium: "text-amber border-amber/30 bg-amber/10", high: "text-down border-down/30 bg-down/10",
};

// Spec §3: Copper, Aluminium, Steel, USD/INR, freight are Stardrive's actual material
// exposure — everything else Alpha Vantage/Frankfurter offer (EUR/GBP/CNY, etc.) is
// deliberately excluded from this page per §16 ("don't show a card merely because an
// API provides it").
const MATERIAL_COMMODITY_KEYS = ["copper", "aluminum", "oil"];
const COMMODITY_TONE: Record<string, string> = { copper: "#FFB347", aluminum: "#8B94B5", oil: "#7B78FF" };
const COMMODITY_LABEL: Record<string, string> = { copper: "Copper (Global Avg)", aluminum: "Aluminum (Global Avg)", oil: "Crude Oil (WTI)" };

export default function MarketBusinessIntelligence() {
  const { data, isLoading, isError, error, refetch, isFetching } = useMarketIntelligence();
  const { data: commodities } = useCommodities();

  if (isLoading) return <DashboardSkeleton />;

  if (isError || !data) {
    const message = (error as any)?.response?.data?.detail || (error as Error)?.message || "Unknown error";
    return (
      <div className="panel p-6 space-y-3">
        <div className="flex items-center gap-2 text-down">
          <AlertTriangle size={16} />
          <span className="text-sm font-semibold">Couldn't load Market &amp; Business Intelligence</span>
        </div>
        <p className="text-xs text-mute font-mono">{message}</p>
        <button onClick={() => refetch()} disabled={isFetching}
          className="text-[11px] font-semibold px-3 py-1.5 rounded-lg text-cyan bg-cyan/10 border border-cyan/25 hover:bg-cyan/20 transition-colors disabled:opacity-50">
          {isFetching ? "Retrying…" : "Retry"}
        </button>
      </div>
    );
  }

  const {
    executive_brief, opportunities, emerging_opportunities, material_margin,
    core_sectors, market_signals, competitors, policy_tenders, macro_logistics,
  } = data;

  return (
    <div className="space-y-6 animate-rise">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Market &amp; Business Intelligence</h1>
        <p className="text-sm text-mute mt-1">
          External developments, ranked by relevance to Stardrive's actual sectors, order history, and product fit.
        </p>
      </div>

      {/* 1. AI Executive Brief */}
      <div className="panel p-5">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="w-8 h-8 rounded-lg bg-grad grid place-items-center shrink-0 shadow-[0_0_16px_rgba(93,140,255,.4)]">
            <Sparkles size={16} className="text-ink" />
          </div>
          <span className="text-sm font-semibold">AI Executive Brief</span>
        </div>
        {executive_brief.length > 0 ? (
          <div className="space-y-3">
            {executive_brief.map((item, i) => <ExecutiveBriefItem key={i} item={item} />)}
          </div>
        ) : (
          <p className="text-sm text-mute">No material developments to report right now.</p>
        )}
        <p className="text-[10px] text-faint pt-3">
          Ranked deterministically from Stardrive's historical sector performance and real commodity/project data — the AI only phrases what's already been selected.
        </p>
      </div>

      {/* 2. Revenue / Opportunity Intelligence */}
      <div>
        <SectionHeader title="Revenue &amp; Opportunity Intelligence" icon={Target} tone="#3EE6A8" />
        {opportunities.length > 0 ? (
          <div className="grid md:grid-cols-2 gap-3">
            {opportunities.map((o, i) => <OpportunityCard key={i} opportunity={o} />)}
          </div>
        ) : (
          <div className="panel p-4"><p className="text-sm text-mute">No scored opportunities in Stardrive's core sectors right now.</p></div>
        )}
      </div>

      {/* 3. Material & Margin Intelligence */}
      <div>
        <SectionHeader title="Material &amp; Margin Intelligence" icon={Factory} tone="#FFB347" />
        {commodities && MATERIAL_COMMODITY_KEYS.some((k) => commodities[k]?.status === "live") && (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-3">
            {MATERIAL_COMMODITY_KEYS.map((key) => commodities[key] && (
              <CommodityCard key={key} seriesKey={key} label={COMMODITY_LABEL[key]} data={commodities[key]}
                impact={material_margin.find((m) => m.series === key)} tone={COMMODITY_TONE[key]} />
            ))}
          </div>
        )}
        <div className="panel p-4">
          {material_margin.length > 0 ? (
            <div className="space-y-2">
              {material_margin.map((m) => (
                <div key={m.series} className="flex items-start gap-2.5 text-sm">
                  <span className={`text-[9px] font-mono uppercase border rounded px-1.5 py-0.5 mt-0.5 shrink-0 ${RISK_TONE[m.risk_level]}`}>{m.risk_level}</span>
                  <span className="text-slate-300">{m.headline} — {m.business_impact[0]}</span>
                </div>
              ))}
              <p className="text-[10px] text-faint pt-2">{material_margin[0]?.basis}</p>
            </div>
          ) : (
            <p className="text-sm text-mute">No material cost or logistics risk flagged today — configure ALPHA_VANTAGE_API_KEY for live copper/aluminium/oil tracking.</p>
          )}
        </div>
      </div>

      {/* 4. Core Sector Intelligence */}
      <div>
        <SectionHeader title="Core Sector Intelligence" icon={Map} tone="#33D6FF" />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {core_sectors.map((s) => <SectorIntelCard key={s.sector} sector={s} />)}
        </div>
      </div>

      {/* Sourced Market Signals — real news (newsdata.io), filtered/scored deterministically */}
      {market_signals.length > 0 && (
        <div>
          <SectionHeader title="Sourced Market Signals" icon={Newspaper} tone="#FFB347" />
          <div className="panel p-4 space-y-3">
            {market_signals.map((s, i) => <MarketSignalItem key={i} signal={s} />)}
          </div>
        </div>
      )}

      {/* 5. Emerging Opportunities */}
      <div>
        <SectionHeader title="Emerging Opportunities" icon={Sparkles} tone="#7B78FF" />
        {emerging_opportunities.length > 0 ? (
          <div className="grid md:grid-cols-2 gap-3">
            {emerging_opportunities.map((o, i) => <OpportunityCard key={i} opportunity={o} />)}
          </div>
        ) : (
          <div className="panel p-4"><p className="text-sm text-mute">No emerging-market signals right now.</p></div>
        )}
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        {/* 6. Competitor Intelligence */}
        <div>
          <SectionHeader title="Competitor Intelligence" icon={Swords} tone="#FF7A93" />
          <div className="panel p-4 space-y-3">
            {competitors.map((c, i) => (
              <div key={i} className="border-b border-panelEdge last:border-0 pb-3 last:pb-0">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-sm font-medium">{c.name} — {c.move}</span>
                  <StatusBadge status={c.status} />
                </div>
                <p className="text-xs text-mute mt-1">{c.detail}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 7. Government / Policy / Tender Intelligence */}
        <div>
          <SectionHeader title="Government, Policy &amp; Tender Intelligence" icon={Gavel} tone="#FFB347" />
          <div className="panel p-4 space-y-3">
            {policy_tenders.map((g, i) => (
              <div key={i} className="border-b border-panelEdge last:border-0 pb-3 last:pb-0">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-sm font-medium">{g.title}</span>
                  <StatusBadge status={g.status} />
                </div>
                <p className="text-xs text-mute mt-1">{g.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 8. Macro & Logistics Intelligence — compact, only when business-relevant */}
      <div>
        <SectionHeader title="Macro &amp; Logistics Intelligence" icon={TrendingUp} tone="#33D6FF" />
        <div className="grid sm:grid-cols-2 gap-3">
          {macro_logistics.usd_inr && (
            <div className="panel p-4">
              <div className="flex items-start justify-between gap-2">
                <span className="text-[11px] uppercase tracking-widest text-mute">USD / INR</span>
                <StatusBadge status={macro_logistics.usd_inr.status} />
              </div>
              {macro_logistics.usd_inr.status === "live" ? (
                <div className="figure text-2xl font-semibold mt-2 text-cyan">
                  {macro_logistics.usd_inr.rate?.toLocaleString()}
                </div>
              ) : (
                <p className="text-xs text-faint mt-2">Affects imported raw-material cost and export conversion — configure ALPHA_VANTAGE_API_KEY to enable.</p>
              )}
            </div>
          )}
          <div className="panel p-4">
            <div className="flex items-center gap-2 mb-1">
              <Cloud size={13} className="text-mute" />
              <span className="text-[11px] uppercase tracking-widest text-mute">Logistics Risk</span>
            </div>
            {macro_logistics.logistics_risk_hubs.length > 0 ? (
              <div className="flex items-start gap-2 mt-2">
                <AlertTriangle size={14} className="text-down mt-0.5 shrink-0" />
                <p className="text-xs text-slate-300">
                  {macro_logistics.logistics_risk_hubs.map((h) => h.hub).join(", ")} flagged for weather risk in the next 3 days — review inbound/outbound shipping schedules.
                </p>
              </div>
            ) : (
              <p className="text-xs text-faint mt-2">No logistics hubs flagged for weather risk right now.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
