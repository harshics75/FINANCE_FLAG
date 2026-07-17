import { DashboardSkeleton } from "../components/ui/Skeleton";
import { ChartPanel, MultiLine } from "../components/charts/TrendChart";
import { useDashboard } from "../hooks/useDashboard";

export default function WorkingCapital() {
  const { data, isLoading } = useDashboard("working_capital");
  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold tracking-tight">Working Capital</h1>
      <div className="grid md:grid-cols-2 gap-4">
        <ChartPanel title="Receivables / Payables / Inventory">
          <MultiLine kind="bar" series={[
            { name: "Receivables", data: p.receivables ?? [] },
            { name: "Payables", data: p.payables ?? [] },
            { name: "Inventory", data: p.inventory ?? [] },
          ]} />
        </ChartPanel>
        <ChartPanel title="DSO vs DPO (days)">
          <MultiLine series={[
            { name: "DSO", data: p.dso ?? [] },
            { name: "DPO", data: p.dpo ?? [] },
          ]} />
        </ChartPanel>
        <ChartPanel title="Cash Conversion Cycle (days)">
          <MultiLine kind="area" series={[{ name: "CCC", data: p.ccc ?? [] }]} />
        </ChartPanel>
      </div>
      {p.summary && (
        <div className="panel p-5">
          <h3 className="text-xs uppercase tracking-widest text-mute mb-3">Working Capital Analysis</h3>
          <p className="text-sm leading-relaxed whitespace-pre-line">{p.summary}</p>
        </div>
      )}
    </div>
  );
}
