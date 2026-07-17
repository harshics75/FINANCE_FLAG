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
        <ChartPanel title="Liquidity (Current Ratio)">
          <MultiLine series={[{ name: "Current Ratio", data: p.current_ratio ?? [] }]} />
        </ChartPanel>
      </div>
    </div>
  );
}
