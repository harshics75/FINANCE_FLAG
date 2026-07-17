import { DashboardSkeleton } from "../components/ui/Skeleton";
import { ChartPanel, MultiLine } from "../components/charts/TrendChart";
import { useDashboard } from "../hooks/useDashboard";

export default function CashFlowDashboard() {
  const { data, isLoading } = useDashboard("cash_flow");
  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold tracking-tight">Cash Flow</h1>
      <div className="grid md:grid-cols-2 gap-4">
        <ChartPanel title="Operating / Investing / Financing">
          <MultiLine kind="bar" series={[
            { name: "Operating", data: p.operating ?? [] },
            { name: "Investing", data: p.investing ?? [] },
            { name: "Financing", data: p.financing ?? [] },
          ]} />
        </ChartPanel>
        <ChartPanel title="Cash Position">
          <MultiLine kind="area" series={[{ name: "Cash", data: p.cash ?? [] }]} />
        </ChartPanel>
        <ChartPanel title="Liquidity (Current vs Quick Ratio)">
          <MultiLine series={[
            { name: "Current Ratio", data: p.current_ratio ?? [] },
            { name: "Quick Ratio", data: p.quick_ratio ?? [] },
          ]} />
        </ChartPanel>
        <ChartPanel title="Debt to Equity">
          <MultiLine kind="bar" series={[{ name: "Debt to Equity", data: p.debt_to_equity ?? [] }]} />
        </ChartPanel>
      </div>
      {p.summary && (
        <div className="panel p-5">
          <h3 className="text-xs uppercase tracking-widest text-mute mb-3">Cash Flow &amp; Liquidity Analysis</h3>
          <p className="text-sm leading-relaxed whitespace-pre-line">{p.summary}</p>
        </div>
      )}
    </div>
  );
}
