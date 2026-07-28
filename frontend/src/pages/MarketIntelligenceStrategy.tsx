import { useNavigate } from "react-router-dom";
import {
  ExternalLink, Gavel, Lightbulb, Map, Newspaper, Sparkles, Swords, Target, TrendingUp,
} from "lucide-react";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import { SectionHeader } from "../components/ui/InsightCard";
import StatusBadge from "../components/ui/StatusBadge";
import EconomicIndicatorCard from "../components/ui/EconomicIndicatorCard";
import {
  useBusinessImpact, useCompetitors, useEconomicIndicators, useGovernmentItems, useInfrastructureProjects,
  useManufacturingNews, useTradeIntelligence,
} from "../hooks/useDashboard";

const TRADE_KEYS = ["gdp_growth", "manufacturing_value_added", "exports_pct_gdp", "imports_pct_gdp", "gdp_growth_outlook", "world_gdp_growth"];

const RELEVANCE_TONE: Record<string, string> = {
  high: "text-up border-up/30 bg-up/10", medium: "text-amber border-amber/30 bg-amber/10", low: "text-mute border-panelEdge",
};

export default function MarketIntelligenceStrategy() {
  const { data: infra, isLoading } = useInfrastructureProjects();
  const { data: impacts } = useBusinessImpact();
  const { data: competitors } = useCompetitors();
  const { data: gov } = useGovernmentItems();
  const { data: trade } = useEconomicIndicators();
  const { data: tradeIntel } = useTradeIntelligence();
  const { data: mfgNews } = useManufacturingNews();
  const navigate = useNavigate();

  if (isLoading) return <DashboardSkeleton />;

  const gnewsConfigured = mfgNews && mfgNews[0]?.status !== "not_configured";
  const stateGroups = (infra ?? []).reduce<Record<string, typeof infra>>((acc, p) => {
    (acc[p.state ?? "Other"] ??= []).push(p);
    return acc;
  }, {});
  const maxScore = Math.max(1, ...(infra ?? []).map((p) => p.opportunity_score));
  const topOpportunities = [...(infra ?? [])].sort((a, b) => b.opportunity_score - a.opportunity_score).slice(0, 3);

  return (
    <div className="space-y-6 animate-rise">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Market Intelligence — Strategy</h1>
        <p className="text-sm text-mute mt-1">For CEO, Sales, Business Development &amp; Strategy — where the opportunities and risks are.</p>
      </div>

      {/* AI Executive Brief */}
      <div className="panel p-5">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="w-8 h-8 rounded-lg bg-grad grid place-items-center shrink-0 shadow-[0_0_16px_rgba(93,140,255,.4)]">
            <Sparkles size={16} className="text-ink" />
          </div>
          <span className="text-sm font-semibold">AI Executive Brief</span>
        </div>
        <div className="space-y-2">
          {(impacts ?? []).slice(0, 3).map((i) => (
            <p key={i.series} className="text-sm text-slate-300">{i.headline} — {i.business_impact[0]}</p>
          ))}
          {topOpportunities.map((p) => (
            <p key={p.name} className="text-sm text-slate-300">
              <span className="text-up font-medium">{p.name}</span> ({p.state}) — opportunity score {p.opportunity_score}. Potential Busduct System opportunity.
            </p>
          ))}
        </div>
        <p className="text-[10px] text-faint pt-3">Built from real commodity/weather data plus the illustrative project pipeline below — see each card's source badge.</p>
      </div>

      {/* Infrastructure Projects + Heat Map */}
      <div>
        <SectionHeader title="Infrastructure Opportunities Across India" icon={Map} tone="#3EE6A8" />
        <div className="panel p-4 mb-3">
          <p className="text-[10px] uppercase tracking-widest text-faint mb-2.5">Project density by state (demo data)</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(stateGroups).map(([state, projects]) => {
              const score = (projects ?? []).reduce((s, p) => s + p.opportunity_score, 0);
              const intensity = Math.min(1, score / (maxScore * 2));
              return (
                <div key={state} className="rounded-lg px-3 py-2 border border-panelEdge"
                  style={{ background: `rgba(62,230,168,${0.06 + intensity * 0.22})` }}>
                  <div className="text-xs font-medium">{state}</div>
                  <div className="text-[10px] text-mute">{projects?.length} project{projects && projects.length > 1 ? "s" : ""}</div>
                </div>
              );
            })}
          </div>
        </div>
        <div className="grid md:grid-cols-2 gap-3">
          {(infra ?? []).map((p, i) => (
            <div key={i} className="panel p-4">
              <div className="flex items-start justify-between gap-2">
                <span className="text-sm font-medium">{p.name}</span>
                <StatusBadge status={p.status} />
              </div>
              <p className="text-xs text-mute mt-1">{p.state}, {p.country} · {p.sector} · {p.stage}</p>
              <div className="flex items-center justify-between mt-3">
                <span className="figure text-lg text-up">₹{p.value_cr.toLocaleString()} Cr</span>
                <span className="text-xs text-mute">Opportunity <span className="text-cyan font-mono">{p.opportunity_score}</span></span>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <span className={`text-[9px] font-mono uppercase border rounded px-1.5 py-0.5 ${RELEVANCE_TONE[p.busduct_relevance ?? "low"]}`}>
                  {p.busduct_relevance ?? "low"} busduct relevance
                </span>
              </div>
              <p className="text-[10px] text-faint mt-2">Demand: {p.material_demand.join(", ")} · Future: {p.future_integration}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Opportunity Intelligence */}
      <div>
        <SectionHeader title="Opportunity Intelligence" icon={Target} tone="#33D6FF" />
        <div className="grid md:grid-cols-3 gap-3">
          {topOpportunities.map((p, i) => (
            <div key={i} className="panel p-4 border border-cyan/20">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb size={14} className="text-cyan" />
                <span className="text-xs uppercase tracking-widest text-cyan">Top Opportunity</span>
              </div>
              <p className="text-sm font-medium">{p.name}</p>
              <p className="text-xs text-mute mt-1">{p.sector} · {p.state} · ₹{p.value_cr.toLocaleString()} Cr</p>
              <button onClick={() => navigate("/chat", { state: { initialPrompt: `Draft an outreach plan for pursuing the "${p.name}" project as a Busduct System supplier.` } })}
                className="mt-3 flex items-center gap-1.5 text-[11px] font-semibold px-3 py-1.5 rounded-lg text-cyan bg-cyan/10 border border-cyan/25 hover:bg-cyan/20 transition-colors">
                <Sparkles size={11} /> Draft Outreach Plan
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        {/* Competitor Intelligence */}
        <div>
          <SectionHeader title="Competitor Intelligence" icon={Swords} tone="#FF7A93" />
          <div className="panel p-4 space-y-3">
            {(competitors ?? []).map((c, i) => (
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

        {/* Government & Policy Intelligence */}
        <div>
          <SectionHeader title="Government & Policy Intelligence" icon={Gavel} tone="#FFB347" />
          <div className="panel p-4 space-y-3">
            {(gov ?? []).map((g, i) => (
              <div key={i} className="border-b border-panelEdge last:border-0 pb-3 last:pb-0">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-sm font-medium">{g.title}</span>
                  <StatusBadge status={g.status} />
                </div>
                <p className="text-xs text-mute mt-1">{g.detail}</p>
              </div>
            ))}
            {tradeIntel?.data_gov_in?.map((g, i) => (
              <div key={`gdi-${i}`} className="border-b border-panelEdge last:border-0 pb-3 last:pb-0">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-sm font-medium">{g.title}</span>
                  <StatusBadge status={g.status} />
                </div>
                <p className="text-xs text-mute mt-1">{g.future_integration}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Trade Intelligence */}
      <div>
        <SectionHeader title="Trade & Economy Intelligence" icon={TrendingUp} tone="#7B78FF" />
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-3">
          {TRADE_KEYS.map((key) => trade?.[key] && <EconomicIndicatorCard key={key} data={trade[key]} tone="#7B78FF" />)}
        </div>
        <div className="panel p-4">
          <p className="text-[10px] uppercase tracking-widest text-faint mb-2">Granular commodity trade (Copper/Aluminium imports, electrical equipment)</p>
          <div className="grid sm:grid-cols-3 gap-2.5">
            {tradeIntel && Object.values(tradeIntel.comtrade).map((c, i) => (
              <div key={i} className="flex items-center justify-between text-xs border border-panelEdge rounded-lg px-3 py-2">
                <span className="text-slate-300">{c.name}</span>
                <StatusBadge status={c.status} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Industry / Electrical Market News */}
      <div>
        <SectionHeader title="Electrical & Industrial Market News" icon={Newspaper} tone="#33D6FF" />
        <div className="panel p-4">
          {!gnewsConfigured ? (
            <div className="flex items-center justify-between">
              <p className="text-sm text-mute">Configure GNEWS_API_KEY for curated electrical/industrial market news.</p>
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
    </div>
  );
}
