import KpiCard from "../components/ui/KpiCard";
import Gauge from "../components/ui/Gauge";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import { ChartPanel, MultiLine } from "../components/charts/TrendChart";
import { useDashboard } from "../hooks/useDashboard";

export default function ExecutiveOverview() {
  const { data, isLoading } = useDashboard("executive");
  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};
  const kpis = p.kpis ?? {};

  return (
    <div className="space-y-4">
      <header className="flex items-end justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Executive Overview</h1>
          {p.headline && <p className="text-sm text-mute mt-1">{p.headline}</p>}
        </div>
        <div className="flex gap-6">
          <Gauge value={p.business_health_score} label="Business Health" />
          <Gauge value={p.risk_score != null ? 100 - p.risk_score : null} label="Risk Safety" />
        </div>
      </header>

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
          <h3 className="text-xs uppercase tracking-widest text-mute mb-3">Executive Summary</h3>
          <p className="text-sm leading-relaxed whitespace-pre-line">{p.summary}</p>
        </div>
      )}
    </div>
  );
}
