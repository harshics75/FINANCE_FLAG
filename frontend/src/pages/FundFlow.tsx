import { useNavigate } from "react-router-dom";
import {
  Activity, Banknote, Boxes, Clock3, CreditCard, Droplet, Gauge as GaugeIcon, Lightbulb,
  Recycle, Scale, Sparkles, TrendingDown, Users,
} from "lucide-react";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import { formatNum } from "../components/ui/KpiCard";
import Gauge from "../components/ui/Gauge";
import IntelligenceCard from "../components/ui/IntelligenceCard";
import InsightCard, { SectionHeader } from "../components/ui/InsightCard";
import TypingReveal from "../components/ui/TypingReveal";
import LiveThinkingPanel from "../components/ui/LiveThinkingPanel";
import { useDashboard } from "../hooks/useDashboard";
import { useAnalysisRun } from "../contexts/AnalysisRunContext";

const FUND_FLOW_KEYWORDS = [
  "cash", "liquidity", "collection", "payment", "inventory", "vendor", "capex", "receivable",
  "dso", "dpo", "payable", "working capital", "cash conversion",
];

// A real ratio (current, quick, debt-to-equity) should never run into the thousands —
// that only happens when mismatched-scale source documents got divided against each
// other. Flag it rather than display a nonsense figure at face value.
function formatRatio(value: number | null | undefined, suffix: string): string | undefined {
  if (value == null) return undefined;
  if (Math.abs(value) > 1000) return "Data anomaly";
  return `${value}${suffix}`;
}

// A real day-count metric (DSO/DPO/CCC) should never run into the thousands, and a
// genuine period-over-period change should never run into the thousands of percent —
// that only happens when mismatched-scale source documents got divided against each
// other. Flag it rather than display a nonsense figure at face value.
function trend(series: any[]): { value: number | null; delta: string | undefined; anomaly: boolean } {
  if (!series?.length) return { value: null, delta: undefined, anomaly: false };
  const value = series[series.length - 1].value;
  if (series.length < 2) return { value, delta: undefined, anomaly: false };
  const prev = series[series.length - 2].value;
  if (!prev) return { value, delta: undefined, anomaly: false };
  const pct = ((value - prev) / Math.abs(prev)) * 100;
  if (Math.abs(pct) > 1000) return { value, delta: undefined, anomaly: true };
  return { value, delta: `${pct > 0 ? "+" : ""}${pct.toFixed(1)}% vs prior period`, anomaly: false };
}

function formatDays(t: { value: number | null; anomaly: boolean }): string {
  if (t.value == null) return "—";
  if (t.anomaly || Math.abs(t.value) > 3650) return "Data anomaly";
  return `${t.value} days`;
}

export default function FundFlow() {
  const { data, isLoading } = useDashboard("fund_flow");
  const { data: forecastData } = useDashboard("forecast");
  const { data: insightsData } = useDashboard("insights");
  const { isRunning, startRun } = useAnalysisRun();
  const navigate = useNavigate();

  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};
  const forecast = forecastData?.payload ?? {};
  const insights = insightsData?.payload ?? {};

  const last = (arr: any[]) => (arr?.length ? arr[arr.length - 1].value : null);
  const askAbout = (prompt: string) => navigate("/chat", { state: { initialPrompt: prompt } });

  const receivables = trend(p.receivables);
  const payables = trend(p.payables);
  const inventory = trend(p.inventory);
  const dso = trend(p.dso);
  const dpo = trend(p.dpo);
  const ccc = trend(p.ccc);

  const recommendations = ((insights.recommendations ?? []) as any[])
    .filter((r) => FUND_FLOW_KEYWORDS.some((k) => `${r.action} ${r.rationale}`.toLowerCase().includes(k)))
    .filter((r, i, arr) => arr.findIndex((o) => o.action === r.action) === i)
    .slice(0, 6);

  const journeyPoints = [
    { label: "Today", value: forecast.today?.cash },
    ...(forecast.milestones ?? []).map((m: any) => ({ label: m.label, value: m.cash })),
  ];

  const suggestions = [
    "Why has DSO increased?",
    "How can we improve working capital?",
    "Predict next quarter's cash conversion cycle.",
    "Generate a CFO action plan for fund flow.",
  ];

  return (
    <div className="grid lg:grid-cols-[1fr_300px] gap-4 items-start animate-rise">
      <div className="space-y-6 min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight">Fund Flow Intelligence</h1>

        {/* Section 1 — Management Health */}
        <div className="panel p-5">
          <div className="flex items-center gap-2.5 mb-4">
            <div className="w-8 h-8 rounded-lg bg-grad grid place-items-center shrink-0 shadow-[0_0_16px_rgba(93,140,255,.4)]">
              <Banknote size={16} className="text-ink" />
            </div>
            <span className="text-sm font-semibold">Stardrive Fund Flow Copilot</span>
          </div>
          <div className="flex gap-6 mb-4 flex-wrap">
            <Gauge value={p.liquidity_health_score} label="Liquidity Health" />
            <Gauge value={p.collection_health_score} label="Collection Health" />
            <Gauge value={p.obligation_health_score} label="Obligation Health" />
          </div>
          {p.cash_flow_summary || p.working_capital_summary ? (
            <div className="space-y-2">
              {p.cash_flow_summary && <TypingReveal text={p.cash_flow_summary} className="text-sm leading-relaxed text-slate-200" />}
              {p.working_capital_summary && <p className="text-sm leading-relaxed text-slate-200">{p.working_capital_summary}</p>}
            </div>
          ) : (
            <p className="text-sm text-mute">Run an analysis to generate a fund flow narrative from your uploaded documents.</p>
          )}
        </div>

        {/* Section 2 — Cash Position */}
        <div>
          <SectionHeader title="Cash Position" icon={Droplet} tone="#33D6FF" confidence={p.confidence} />
          <div className="grid md:grid-cols-2 gap-3">
            <IntelligenceCard icon={Activity} tone="#3EE6A8" title="Operating Cash Flow" value={formatNum(last(p.operating))}
              explanation="Cash generated from core business operations." confidence={p.confidence} onDeepDive={() => askAbout("Explain the operating cash flow trend.")} />
            <IntelligenceCard icon={TrendingDown} tone="#7B78FF" title="Investing Cash Flow" value={formatNum(last(p.investing))}
              explanation="Cash used for or generated from long-term investments." confidence={p.confidence} onDeepDive={() => askAbout("Explain the investing cash flow.")} />
            <IntelligenceCard icon={Banknote} tone="#FFB347" title="Financing Cash Flow" value={formatNum(last(p.financing))}
              explanation="Cash from debt, equity, and financing activities." confidence={p.confidence} onDeepDive={() => askAbout("Explain the financing cash flow.")} />
            <IntelligenceCard icon={Droplet} tone="#33D6FF" title="Liquidity" value={formatRatio(last(p.current_ratio), "x current") ?? "—"}
              explanation={formatRatio(last(p.quick_ratio), "x quick ratio")}
              confidence={p.confidence} onDeepDive={() => askAbout("Explain the company's liquidity position.")} />
            <IntelligenceCard icon={Scale} tone="#FF7A93" title="Debt" value={formatRatio(last(p.debt_to_equity), "x D/E") ?? "—"}
              explanation="Total debt relative to shareholder equity." confidence={p.confidence} onDeepDive={() => askAbout("Explain the company's debt position.")} />
            <IntelligenceCard icon={GaugeIcon} tone="#FFB347" title="Burn Rate & Runway"
              value={p.burn_rate_monthly ? `${formatNum(p.burn_rate_monthly)}/mo` : "Not burning cash"}
              explanation={p.runway_months != null ? `≈ ${p.runway_months} months of runway at current burn` : "Cash is stable or growing period-over-period."}
              confidence={p.confidence} onDeepDive={() => askAbout("Explain the company's cash burn rate and runway.")} />
          </div>
        </div>

        {/* Section 3 — Working Capital */}
        <div>
          <SectionHeader title="Working Capital" icon={Recycle} tone="#3EE6A8" confidence={p.confidence} />
          <div className="grid md:grid-cols-2 gap-3">
            <IntelligenceCard icon={Users} tone="#33D6FF" title="Receivables Intelligence" value={formatNum(receivables.value)}
              explanation={receivables.delta} confidence={p.confidence} onDeepDive={() => askAbout("Explain the trend in receivables.")} />
            <IntelligenceCard icon={Boxes} tone="#7B78FF" title="Inventory Intelligence" value={formatNum(inventory.value)}
              explanation={inventory.delta} confidence={p.confidence} onDeepDive={() => askAbout("Explain the trend in inventory.")} />
            <IntelligenceCard icon={CreditCard} tone="#FFB347" title="Payables Intelligence" value={formatNum(payables.value)}
              explanation={payables.delta} confidence={p.confidence} onDeepDive={() => askAbout("Explain the trend in payables.")} />
            <IntelligenceCard icon={Clock3} tone="#FF7A93" title="DSO Intelligence" value={formatDays(dso)}
              explanation={dso.delta} impact={!dso.anomaly && dso.value != null && dso.value > 60 ? "Elevated — collections may be slowing" : undefined}
              confidence={p.confidence} onDeepDive={() => askAbout("Why has DSO changed and how can we improve it?")} />
            <IntelligenceCard icon={Clock3} tone="#3EE6A8" title="DPO Intelligence" value={formatDays(dpo)}
              explanation={dpo.delta} confidence={p.confidence} onDeepDive={() => askAbout("Explain the DPO trend.")} />
            <IntelligenceCard icon={Recycle} tone="#33D6FF" title="Cash Conversion Intelligence" value={formatDays(ccc)}
              explanation={ccc.delta} confidence={p.confidence} onDeepDive={() => askAbout("Explain the cash conversion cycle trend.")} />
          </div>
        </div>

        {/* Section 4 — Future Cash Journey */}
        {forecast.available && (
          <div>
            <SectionHeader title="Future Cash Journey" icon={Sparkles} tone="#33D6FF" confidence={forecast.confidence} />
            <div className="panel p-4">
              <p className="text-xs text-mute mb-4">Trend-based projection from {forecast.periods_used} historical period(s) — not an AI prediction.</p>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                {journeyPoints.map((pt, i) => (
                  <div key={i} className="text-center">
                    <div className="text-[10px] uppercase tracking-widest text-faint mb-1">{pt.label}</div>
                    <div className="figure text-sm">{pt.value != null ? formatNum(pt.value) : "—"}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Section 5 — AI Recommendations */}
        {recommendations.length > 0 && (
          <div>
            <SectionHeader title="AI Fund Flow Recommendations" icon={Lightbulb} tone="#FFB347" />
            <div className="grid md:grid-cols-2 gap-3">
              {recommendations.map((r: any, i: number) => (
                <InsightCard key={i} icon={Lightbulb} tone={r.priority === "high" ? "#FF7A93" : "#FFB347"}
                  title={r.action} cause={r.rationale} impact={r.expected_impact}
                  tag={`${r.priority} priority · ${r.timeframe}`}
                  onExplain={() => askAbout(`Draft an implementation plan for: "${r.action}"`)} />
              ))}
            </div>
          </div>
        )}

        {/* Section 6 — Ask Stardrive */}
        <div>
          <SectionHeader title="Ask Stardrive" icon={Sparkles} tone="#7B78FF" />
          <div className="panel p-4 flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button key={s} onClick={() => askAbout(s)}
                className="text-xs text-mute border border-panelEdge rounded-full px-3.5 py-1.5 hover:text-slate-200 hover:border-panelEdgeHi transition-colors">
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <LiveThinkingPanel title="Live Fund Flow Analysis" />
        {!isRunning && (
          <button onClick={() => startRun()}
            className="w-full rounded-lg bg-grad text-ink text-sm font-semibold px-4 py-2.5 hover:brightness-110 transition-all">
            Run analysis
          </button>
        )}
      </div>
    </div>
  );
}
