import { useNavigate } from "react-router-dom";
import {
  Activity, Banknote, Bot, Droplet, Gauge as GaugeIcon, Lightbulb, Scale, Sparkles, TrendingDown, Wallet,
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

const CASH_KEYWORDS = ["cash", "liquidity", "collection", "payment", "inventory", "vendor", "capex", "receivable"];

// A real ratio (current, quick, debt-to-equity) should never run into the thousands —
// that only happens when mismatched-scale source documents got divided against each
// other. Flag it rather than display a nonsense figure at face value.
function formatRatio(value: number | null | undefined, suffix: string): string | undefined {
  if (value == null) return undefined;
  if (Math.abs(value) > 1000) return "Data anomaly";
  return `${value}${suffix}`;
}

export default function CashFlowDashboard() {
  const { data, isLoading } = useDashboard("cash_flow");
  const { data: forecastData } = useDashboard("forecast");
  const { data: insightsData } = useDashboard("insights");
  const { isRunning, startRun } = useAnalysisRun();
  const navigate = useNavigate();

  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};
  const forecast = forecastData?.payload ?? {};
  const insights = insightsData?.payload ?? {};

  const last = (arr: any[]) => (arr?.length ? arr[arr.length - 1].value : null);
  const treasuryActions = ((insights.recommendations ?? []) as any[])
    .filter((r) => CASH_KEYWORDS.some((k) => `${r.action} ${r.rationale}`.toLowerCase().includes(k)))
    .slice(0, 4);

  const askAbout = (prompt: string) => navigate("/chat", { state: { initialPrompt: prompt } });
  const journeyPoints = [
    { label: "Today", value: forecast.today?.cash },
    ...(forecast.milestones ?? []).map((m: any) => ({ label: m.label, value: m.cash })),
  ];

  return (
    <div className="grid lg:grid-cols-[1fr_300px] gap-4 items-start animate-rise">
      <div className="space-y-6 min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight">Cash Flow Intelligence</h1>

        {/* Section 1 — AI Cash Flow Copilot */}
        <div className="panel p-5">
          <div className="flex items-center gap-2.5 mb-4">
            <div className="w-8 h-8 rounded-lg bg-grad grid place-items-center shrink-0 shadow-[0_0_16px_rgba(93,140,255,.4)]">
              <Bot size={16} className="text-ink" />
            </div>
            <span className="text-sm font-semibold">FinSight Treasury Copilot</span>
          </div>
          <div className="flex gap-6 mb-4">
            <Gauge value={p.liquidity_score} label="Liquidity Score" />
            <Gauge value={p.risk_score != null ? 100 - p.risk_score : null} label="Cash Safety" />
          </div>
          {p.summary ? (
            <TypingReveal text={p.summary} className="text-sm leading-relaxed text-slate-200" />
          ) : (
            <p className="text-sm text-mute">Run an analysis to generate a cash flow narrative from your uploaded documents.</p>
          )}
        </div>

        {/* Section 2 — AI Cash Flow Cards */}
        <div>
          <SectionHeader title="AI Cash Flow Cards" icon={Wallet} tone="#33D6FF" confidence={p.confidence} />
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

        {/* Section 3 — Future Cash Journey */}
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

        {/* Section 4 — AI Treasury Advisor */}
        {treasuryActions.length > 0 && (
          <div>
            <SectionHeader title="AI Treasury Advisor" icon={Lightbulb} tone="#FFB347" />
            <div className="grid md:grid-cols-2 gap-3">
              {treasuryActions.map((r: any, i: number) => (
                <InsightCard key={i} icon={Lightbulb} tone={r.priority === "high" ? "#FF7A93" : "#FFB347"}
                  title={r.action} cause={r.rationale} impact={r.expected_impact}
                  tag={`${r.priority} priority · ${r.timeframe}`}
                  onExplain={() => askAbout(`Draft an implementation plan for: "${r.action}"`)} />
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="space-y-4">
        <LiveThinkingPanel title="Live Treasury Analysis" />
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
