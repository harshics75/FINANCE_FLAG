import { useNavigate } from "react-router-dom";
import {
  Bot, DollarSign, FileText, Lightbulb, MessageCircle, Percent, Sparkles, TrendingUp,
} from "lucide-react";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import { formatNum } from "../components/ui/KpiCard";
import IntelligenceCard from "../components/ui/IntelligenceCard";
import InsightCard, { SectionHeader } from "../components/ui/InsightCard";
import StoryTimeline, { type StoryStep } from "../components/ui/StoryTimeline";
import TypingReveal from "../components/ui/TypingReveal";
import LiveThinkingPanel from "../components/ui/LiveThinkingPanel";
import { useDashboard } from "../hooks/useDashboard";
import { useAnalysisRun } from "../contexts/AnalysisRunContext";

interface PoP { metric: string; prior: number | null; current: number | null; change_pct: number | null; commentary: string; }
interface Rec { action: string; rationale: string; priority: string; expected_impact: string; timeframe: string; }

function findPop(pop: PoP[], ...keywords: string[]): PoP | undefined {
  return pop.find((p) => keywords.some((k) => p.metric?.toLowerCase().includes(k)));
}

// A real percentage metric should never run into the millions — that magnitude only
// shows up when mismatched-scale source documents got divided against each other.
// Flag it rather than display a nonsense figure at face value.
function formatPct(value: number | null | undefined): string {
  if (value == null) return "—";
  if (Math.abs(value) > 1000) return "Data anomaly";
  return `${value.toFixed(1)}%`;
}

export default function FinancialPerformance() {
  const { data, isLoading } = useDashboard("performance");
  const { data: execData } = useDashboard("executive");
  const { data: insightsData } = useDashboard("insights");
  const { data: forecastData } = useDashboard("forecast");
  const { isRunning, startRun } = useAnalysisRun();
  const navigate = useNavigate();

  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};
  const exec = execData?.payload ?? {};
  const insights = insightsData?.payload ?? {};
  const forecast = forecastData?.payload ?? {};
  const pop: PoP[] = p.period_over_period ?? [];
  const recommendations: Rec[] = (insights.recommendations ?? []).slice(0, 5);
  const confidence: number | null = p.confidence ?? null;

  const revPop = findPop(pop, "revenue");
  const profitPop = findPop(pop, "profit", "net profit", "pat");
  const marginPop = findPop(pop, "margin");
  const growthPop = findPop(pop, "growth");

  const forecast90 = (forecast.milestones ?? []).find((m: any) => m.days === 90);
  const askAbout = (prompt: string) => navigate("/chat", { state: { initialPrompt: prompt } });

  const storySteps: StoryStep[] = [];
  if (p.profitability_assessment) storySteps.push({ label: forecast.base_period ?? "Latest Period", text: p.profitability_assessment, tone: "#7B78FF" });
  if (revPop?.commentary) storySteps.push({ label: "Revenue", text: revPop.commentary, tone: "#33D6FF" });
  if (marginPop?.commentary) storySteps.push({ label: "Margins", text: marginPop.commentary, tone: "#FFB347" });
  if (profitPop?.commentary) storySteps.push({ label: "Profit", text: profitPop.commentary, tone: "#FF7A93" });
  if (recommendations[0]) storySteps.push({ label: "AI Recommendation", text: `${recommendations[0].action} — ${recommendations[0].rationale}`, tone: "#3EE6A8" });

  const hasNarrative = !!p.profitability_assessment;

  return (
    <div className="grid lg:grid-cols-[1fr_300px] gap-4 items-start animate-rise">
      <div className="space-y-6 min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight">Financial Performance</h1>

        {/* Section 1 — AI Executive Insight */}
        <div className="panel p-5">
          <div className="flex items-center gap-2.5 mb-3">
            <div className="w-8 h-8 rounded-lg bg-grad grid place-items-center shrink-0 shadow-[0_0_16px_rgba(93,140,255,.4)]">
              <Bot size={16} className="text-ink" />
            </div>
            <span className="text-sm font-semibold">FinSight Analyst</span>
            {confidence != null && <span className="text-[10px] font-mono text-faint ml-auto">{confidence}% confidence</span>}
          </div>
          {hasNarrative ? (
            <TypingReveal text={p.profitability_assessment} className="text-sm leading-relaxed text-slate-200" />
          ) : (
            <p className="text-sm text-mute">Run an analysis to generate a performance narrative from your uploaded documents.</p>
          )}
          <div className="flex flex-wrap gap-2 mt-4">
            <button onClick={() => askAbout("Explain the financial performance analysis in more detail.")}
              className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-cyan/10 text-cyan border border-cyan/25 hover:bg-cyan/20 transition-colors">
              <Sparkles size={11} /> Explain
            </button>
            <button onClick={() => navigate("/board-report")}
              className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-amber/10 text-amber border border-amber/25 hover:bg-amber/20 transition-colors">
              <FileText size={11} /> Generate Board Report
            </button>
            <button onClick={() => navigate("/chat")}
              className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-violet/10 text-violet border border-violet/25 hover:bg-violet/20 transition-colors">
              <MessageCircle size={11} /> Ask Follow-up
            </button>
          </div>
        </div>

        {/* Section 2 — AI Performance Intelligence Cards */}
        <div>
          <SectionHeader title="AI Performance Intelligence" icon={Sparkles} tone="#33D6FF" confidence={confidence} />
          <div className="grid md:grid-cols-2 gap-3">
            <IntelligenceCard icon={TrendingUp} tone="#33D6FF" title="Revenue Intelligence"
              value={formatNum(exec.kpis?.revenue)} explanation={revPop?.commentary}
              impact={revPop?.change_pct != null ? `${revPop.change_pct > 0 ? "+" : ""}${revPop.change_pct.toFixed(1)}% vs prior period` : undefined}
              forecast={forecast90?.revenue != null ? `${formatNum(forecast90.revenue)} in 90 days` : undefined}
              confidence={confidence} onDeepDive={() => askAbout("Explain the revenue trend in detail.")} />
            <IntelligenceCard icon={DollarSign} tone="#FF7A93" title="Profit Intelligence"
              value={formatNum(exec.kpis?.net_profit)} explanation={profitPop?.commentary}
              impact={profitPop?.change_pct != null ? `${profitPop.change_pct > 0 ? "+" : ""}${profitPop.change_pct.toFixed(1)}% vs prior period` : undefined}
              forecast={forecast90?.net_profit != null ? `${formatNum(forecast90.net_profit)} in 90 days` : "not projectable"}
              confidence={confidence} onDeepDive={() => askAbout("Explain the profit trend in detail.")} />
            <IntelligenceCard icon={Percent} tone="#FFB347" title="Margin Intelligence"
              value={formatPct(p.gross_margin_series?.at(-1)?.value)}
              explanation={marginPop?.commentary}
              impact={marginPop?.change_pct != null ? `${marginPop.change_pct > 0 ? "+" : ""}${marginPop.change_pct.toFixed(1)}pt vs prior period` : undefined}
              confidence={confidence} onDeepDive={() => askAbout("Explain the margin trend in detail.")} />
            <IntelligenceCard icon={Sparkles} tone="#7B78FF" title="Growth Intelligence"
              value={formatPct(growthPop?.current ?? revPop?.change_pct)}
              explanation={growthPop?.commentary ?? "Growth rate derived from revenue period-over-period change."}
              confidence={confidence} onDeepDive={() => askAbout("Explain the company's growth trajectory.")} />
          </div>
        </div>

        {/* Section 3 — AI Business Story */}
        {storySteps.length > 0 && (
          <div>
            <SectionHeader title="AI Business Story" icon={Sparkles} tone="#7B78FF" />
            <div className="panel p-5">
              <StoryTimeline steps={storySteps} />
            </div>
          </div>
        )}

        {/* Section 4 — Recommendations */}
        {recommendations.length > 0 && (
          <div>
            <SectionHeader title="AI Recommendations" icon={Lightbulb} tone="#FFB347" confidence={insights.recommendation_confidence} />
            <div className="grid md:grid-cols-2 gap-3">
              {recommendations.map((r, i) => (
                <InsightCard key={i} icon={Lightbulb} tone={r.priority === "high" ? "#FF7A93" : r.priority === "medium" ? "#FFB347" : "#8B94B5"}
                  title={r.action} cause={r.rationale} impact={r.expected_impact}
                  tag={`${r.priority} priority · ${r.timeframe}`}
                  onExplain={() => askAbout(`Draft an implementation plan for: "${r.action}" — ${r.rationale}`)} />
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="space-y-4">
        <LiveThinkingPanel />
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
