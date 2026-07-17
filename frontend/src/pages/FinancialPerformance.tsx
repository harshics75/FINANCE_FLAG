import { DashboardSkeleton } from "../components/ui/Skeleton";
import { ChartPanel, MultiLine } from "../components/charts/TrendChart";
import { formatNum } from "../components/ui/KpiCard";
import { useDashboard } from "../hooks/useDashboard";

export default function FinancialPerformance() {
  const { data, isLoading } = useDashboard("performance");
  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};
  const pop: any[] = p.period_over_period ?? [];

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold tracking-tight">Financial Performance</h1>
      <div className="grid md:grid-cols-2 gap-4">
        <ChartPanel title="Revenue vs Net Profit">
          <MultiLine series={[
            { name: "Revenue", data: p.revenue_series ?? [] },
            { name: "Net Profit", data: p.profit_series ?? [] },
          ]} />
        </ChartPanel>
        <ChartPanel title="EBITDA">
          <MultiLine kind="bar" series={[{ name: "EBITDA", data: p.ebitda_series ?? [] }]} />
        </ChartPanel>
        <ChartPanel title="Margins (%)">
          <MultiLine series={[
            { name: "Gross Margin", data: p.gross_margin_series ?? [] },
            { name: "Net Margin", data: p.net_margin_series ?? [] },
          ]} />
        </ChartPanel>
        <div className="panel p-4 overflow-auto">
          <h3 className="text-xs uppercase tracking-widest text-mute mb-3">Period-over-Period</h3>
          {pop.length === 0 ? (
            <p className="text-sm text-mute">Run an analysis to populate the comparison.</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="text-mute text-xs uppercase">
                <tr><th className="text-left py-1">Metric</th><th className="text-right">Prior</th>
                  <th className="text-right">Current</th><th className="text-right">Δ%</th></tr>
              </thead>
              <tbody className="font-mono">
                {pop.map((r, i) => (
                  <tr key={i} className="border-t border-panelEdge">
                    <td className="py-1.5 font-sans">{r.metric}</td>
                    <td className="text-right">{formatNum(r.prior)}</td>
                    <td className="text-right">{formatNum(r.current)}</td>
                    <td className={`text-right ${(r.change_pct ?? 0) >= 0 ? "text-up" : "text-down"}`}>
                      {r.change_pct == null ? "—" : `${r.change_pct > 0 ? "+" : ""}${r.change_pct.toFixed(1)}%`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
