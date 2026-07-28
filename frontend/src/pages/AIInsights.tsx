import { useNavigate } from "react-router-dom";
import {
  CircleCheck, CircleX, Lightbulb, ShieldAlert, Sparkles, Target,
} from "lucide-react";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import InsightCard, { SectionHeader } from "../components/ui/InsightCard";
import { useDashboard } from "../hooks/useDashboard";
import { useAnalysisRun } from "../contexts/AnalysisRunContext";

const PRIORITY_TONE: Record<string, string> = {
  high: "#FF7A93", medium: "#FFB347", low: "#8B94B5",
};

interface Rec { action: string; rationale: string; priority: string; expected_impact: string; timeframe: string; }

function CardGrid({ title, icon, tone, items, cols = 3, navigate, confidence }: {
  title: string; icon: any; tone: string; items: string[]; cols?: number;
  navigate: (prompt: string) => void; confidence?: number | null;
}) {
  if (items.length === 0) return null;
  return (
    <div>
      <SectionHeader title={title} icon={icon} tone={tone} confidence={confidence} />
      <div className={`grid gap-3 ${cols === 3 ? "md:grid-cols-3" : "md:grid-cols-2"}`}>
        {items.map((text, i) => (
          <InsightCard key={i} icon={icon} tone={tone} title={text}
            onExplain={() => navigate(`Explain this in more detail: "${text}"`)} />
        ))}
      </div>
    </div>
  );
}

export default function AIInsights() {
  const { data, isLoading } = useDashboard("insights");
  const navigate = useNavigate();
  const { isRunning, startRun } = useAnalysisRun();

  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};
  const greenFlags: string[] = (p.green_flags ?? []).filter(Boolean);
  const redFlags: string[] = (p.red_flags ?? []).filter(Boolean);
  const criticalInsights: string[] = (p.critical_insights ?? []).filter(Boolean);
  const opportunities: string[] = (p.top_opportunities ?? []).filter(Boolean);
  const risks: string[] = (p.top_risks ?? []).filter(Boolean);
  const recommendations: Rec[] = p.recommendations ?? [];
  const confidence: number | null = p.confidence ?? null;
  const recConfidence: number | null = p.recommendation_confidence ?? null;

  const askAbout = (prompt: string) => navigate("/chat", { state: { initialPrompt: prompt } });

  const nothingYet = greenFlags.length === 0 && redFlags.length === 0 && criticalInsights.length === 0
    && opportunities.length === 0 && risks.length === 0 && recommendations.length === 0;

  return (
    <div className="space-y-6 animate-rise">
      <header className="flex items-center justify-between">
        <div>
          <span className="eyebrow mb-3"><Sparkles size={11} /> 8-node analysis pipeline</span>
          <h1 className="text-2xl font-semibold tracking-tight mt-2">AI Insights</h1>
        </div>
        <button onClick={() => startRun()} disabled={isRunning}
          className="rounded-lg bg-grad text-ink text-sm font-semibold px-4 py-2.5 hover:brightness-110 disabled:opacity-60 transition-all">
          {isRunning ? "Running analysis…" : "Run analysis"}
        </button>
      </header>

      {nothingYet && (
        <div className="panel p-5 text-sm text-mute">
          No analysis has run yet — click "Run analysis" to generate insights from your uploaded documents.
        </div>
      )}

      <CardGrid title="Top 3 Green Flags" icon={CircleCheck} tone="#3EE6A8" items={greenFlags} navigate={askAbout} confidence={confidence} />
      <CardGrid title="Top 3 Red Flags" icon={CircleX} tone="#FF7A93" items={redFlags} navigate={askAbout} confidence={confidence} />
      <CardGrid title="5 Critical Business Insights" icon={Sparkles} tone="#7B78FF" items={criticalInsights} navigate={askAbout} confidence={confidence} />
      <CardGrid title="Top Opportunities" icon={Target} tone="#3EE6A8" items={opportunities} cols={2} navigate={askAbout} />
      <CardGrid title="Top Risks" icon={ShieldAlert} tone="#FF7A93" items={risks} cols={2} navigate={askAbout} />

      {recommendations.length > 0 && (
        <div>
          <SectionHeader title="Recommended Actions" icon={Lightbulb} tone="#FFB347" confidence={recConfidence} />
          <div className="grid md:grid-cols-2 gap-3">
            {recommendations.map((r, i) => (
              <InsightCard key={i} icon={Lightbulb} tone={PRIORITY_TONE[r.priority] ?? "#FFB347"}
                title={r.action} cause={r.rationale} impact={r.expected_impact}
                tag={`${r.priority} priority · ${r.timeframe}`}
                onExplain={() => askAbout(`Explain why this recommendation matters: "${r.action}" — ${r.rationale}`)} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
