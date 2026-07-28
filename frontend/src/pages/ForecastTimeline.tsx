import { AlertCircle, TrendingUp } from "lucide-react";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import { formatNum } from "../components/ui/KpiCard";
import ConfidenceRing from "../components/ui/ConfidenceRing";
import { useDashboard } from "../hooks/useDashboard";

interface Milestone { label: string; days: number; confidence: number; revenue: number | null; net_profit: number | null; cash: number | null; }

export default function ForecastTimeline() {
  const { data, isLoading } = useDashboard("forecast");
  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};

  if (!p.available) {
    return (
      <div className="space-y-4 animate-rise">
        <h1 className="text-2xl font-semibold tracking-tight">Forecast Timeline</h1>
        <div className="panel p-5 flex items-start gap-3 text-sm text-mute">
          <AlertCircle size={16} className="shrink-0 mt-0.5 text-amber" />
          <span>{p.reason ?? "Run an analysis with at least 2 fiscal periods of data to generate a trend projection."}</span>
        </div>
      </div>
    );
  }

  const milestones: Milestone[] = p.milestones ?? [];
  const today = p.today ?? {};

  return (
    <div className="space-y-4 animate-rise">
      <header>
        <span className="eyebrow mb-3"><TrendingUp size={11} /> Trend-based projection — not an AI prediction</span>
        <h1 className="text-2xl font-semibold tracking-tight mt-2">Forecast Timeline</h1>
        <p className="text-sm text-mute mt-1">
          Extrapolates the growth rate observed between your last 2 fiscal periods ({p.base_period}) forward,
          assuming it holds steady. Based on {p.periods_used} historical period{p.periods_used === 1 ? "" : "s"} —
          treat this as a scenario, not a guarantee.
        </p>
      </header>

      <div className="grid md:grid-cols-5 gap-3">
        <div className="panel p-4">
          <span className="text-[11px] uppercase tracking-widest text-mute">Today</span>
          <div className="mt-2 space-y-1">
            <div className="figure text-lg">{formatNum(today.revenue)} <span className="text-[10px] text-mute font-sans">revenue</span></div>
            <div className="figure text-lg">{formatNum(today.cash)} <span className="text-[10px] text-mute font-sans">cash</span></div>
          </div>
        </div>
        {milestones.map((m) => (
          <div key={m.days} className="panel panel-interactive p-4 relative overflow-hidden">
            <span className="absolute inset-x-0 top-0 h-px bg-grad opacity-60" />
            <div className="flex items-center justify-between">
              <span className="text-[11px] uppercase tracking-widest text-mute">{m.label}</span>
              <ConfidenceRing value={m.confidence} tone="#33D6FF" size={26} />
            </div>
            <div className="mt-2 space-y-1">
              <div className="figure text-lg">{m.revenue != null ? formatNum(m.revenue) : "—"} <span className="text-[10px] text-mute font-sans">revenue</span></div>
              <div className="figure text-lg">{m.cash != null ? formatNum(m.cash) : "—"} <span className="text-[10px] text-mute font-sans">cash</span></div>
              <div className="figure text-sm text-mute">
                {m.net_profit != null ? formatNum(m.net_profit) : "not projectable"} <span className="text-[10px] font-sans">net profit</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="panel p-4 text-xs text-mute">
        Confidence reflects how many historical fiscal periods back this projection — not the model's self-assessment.
        A metric shows "not projectable" when it swung between positive and negative, since compound growth from a
        sign change isn't mathematically meaningful.
      </div>
    </div>
  );
}
