import { useNavigate } from "react-router-dom";
import {
  Boxes, Clock3, CreditCard, Lightbulb, Recycle, Sparkles, TrendingUp, Users,
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

const WC_KEYWORDS = ["dso", "dpo", "receivable", "payable", "inventory", "collection", "vendor", "working capital", "cash conversion"];

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

export default function WorkingCapital() {
  const { data, isLoading } = useDashboard("working_capital");
  const { data: insightsData } = useDashboard("insights");
  const { isRunning, startRun } = useAnalysisRun();
  const navigate = useNavigate();

  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};
  const insights = insightsData?.payload ?? {};
  const askAbout = (prompt: string) => navigate("/chat", { state: { initialPrompt: prompt } });

  const receivables = trend(p.receivables);
  const payables = trend(p.payables);
  const inventory = trend(p.inventory);
  const dso = trend(p.dso);
  const dpo = trend(p.dpo);
  const ccc = trend(p.ccc);

  const opportunities = ((insights.recommendations ?? []) as any[])
    .filter((r) => WC_KEYWORDS.some((k) => `${r.action} ${r.rationale}`.toLowerCase().includes(k)));

  const suggestions = [
    "Why has DSO increased?",
    "How can we improve working capital?",
    "Predict next quarter's cash conversion cycle.",
    "Generate a CFO action plan for working capital.",
  ];

  return (
    <div className="grid lg:grid-cols-[1fr_300px] gap-4 items-start animate-rise">
      <div className="space-y-6 min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight">Working Capital Intelligence</h1>

        {/* Section 1 — AI Working Capital Summary */}
        <div className="panel p-5">
          <div className="flex gap-6 mb-4">
            <Gauge value={p.risk_score != null ? 100 - p.risk_score : null} label="Working Capital Safety" />
          </div>
          {p.summary ? (
            <TypingReveal text={p.summary} className="text-sm leading-relaxed text-slate-200" />
          ) : (
            <p className="text-sm text-mute">Run an analysis to generate a working capital narrative from your uploaded documents.</p>
          )}
        </div>

        {/* Section 2 — AI Opportunity Cards */}
        <div>
          <SectionHeader title="AI Opportunity Cards" icon={Sparkles} tone="#33D6FF" confidence={p.confidence} />
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

        {/* Section 3 — Optimization Engine */}
        {opportunities.length > 0 && (
          <div>
            <SectionHeader title="Working Capital Optimization Engine" icon={TrendingUp} tone="#3EE6A8" />
            <div className="grid md:grid-cols-2 gap-3">
              {opportunities.map((r: any, i: number) => (
                <InsightCard key={i} icon={Lightbulb} tone={r.priority === "high" ? "#FF7A93" : "#FFB347"}
                  title={r.action} cause={r.rationale} impact={r.expected_impact}
                  tag={`${r.priority} priority · ${r.timeframe}`}
                  onExplain={() => askAbout(`Draft an implementation plan for: "${r.action}"`)} />
              ))}
            </div>
          </div>
        )}

        {/* Section 4 — Conversational AI */}
        <div>
          <SectionHeader title="Ask FinSight" icon={Sparkles} tone="#7B78FF" />
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
        <LiveThinkingPanel title="Live Working Capital Analysis" />
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
