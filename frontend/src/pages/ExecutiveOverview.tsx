import { Sparkles } from "lucide-react";
import KpiCard from "../components/ui/KpiCard";
import Gauge from "../components/ui/Gauge";
import MarketStrip from "../components/ui/MarketStrip";
import AIAvatarHero from "../components/ui/AIAvatarHero";
import TypingReveal from "../components/ui/TypingReveal";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import { ChartPanel, MultiLine } from "../components/charts/TrendChart";
import { useDashboard } from "../hooks/useDashboard";

function timeAgo(iso?: string): string {
  if (!iso) return "";
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  return hrs < 24 ? `${hrs}h ago` : `${Math.floor(hrs / 24)}d ago`;
}

export default function ExecutiveOverview() {
  const { data, isLoading } = useDashboard("executive");
  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};
  const kpis = p.kpis ?? {};

  return (
    <div className="space-y-4 animate-rise">
      <AIAvatarHero />

      <header className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <span className="eyebrow mb-3"><Sparkles size={11} /> AI-Generated Analysis{data?.generated_at ? ` · updated ${timeAgo(data.generated_at)}` : ""}</span>
          <h1 className="text-2xl font-semibold tracking-tight mt-2">Executive Overview</h1>
          {p.headline && <p className="text-sm text-mute mt-1">{p.headline}</p>}
        </div>
        <div className="flex gap-6">
          <Gauge value={p.business_health_score} label="Business Health" />
          <Gauge value={p.risk_score != null ? 100 - p.risk_score : null} label="Risk Safety" />
        </div>
      </header>

      <MarketStrip />

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <KpiCard label="Revenue" value={kpis.revenue} />
        <KpiCard label="Net Profit" value={kpis.net_profit} />
        <KpiCard label="Cash" value={kpis.cash} />
        <KpiCard label="Working Capital" value={kpis.working_capital} />
        <KpiCard label="EBITDA" value={kpis.ebitda} />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <ChartPanel title="Revenue Trend">
          <MultiLine kind="area" series={[{ name: "Revenue", data: p.revenue_series ?? [] }]} />
        </ChartPanel>
        <ChartPanel title="Net Profit Trend">
          <MultiLine kind="bar" series={[{ name: "Net Profit", data: p.profit_series ?? [] }]} />
        </ChartPanel>
      </div>

      {p.summary && (
        <div className="panel p-5">
          <h3 className="flex items-center gap-2 text-xs uppercase tracking-widest text-mute mb-3">
            <Sparkles size={12} className="text-cyan" /> Here's what I found
          </h3>
          <TypingReveal text={p.summary} />
        </div>
      )}
    </div>
  );
}
