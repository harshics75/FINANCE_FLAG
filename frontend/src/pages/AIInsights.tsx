import { useMutation, useQueryClient } from "@tanstack/react-query";
import { CircleCheck, CircleX, Lightbulb, ShieldAlert, Sparkles, Target } from "lucide-react";
import api from "../services/api";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import { useDashboard } from "../hooks/useDashboard";

function List({ title, icon: Icon, items, tone }: {
  title: string; icon: any; items: any[]; tone: string;
}) {
  return (
    <div className="panel p-4">
      <h3 className={`flex items-center gap-2 text-xs uppercase tracking-widest mb-3 ${tone}`}>
        <Icon size={14} /> {title}
      </h3>
      {items.length === 0 ? <p className="text-sm text-mute">Nothing yet.</p> : (
        <ul className="space-y-2 text-sm">
          {items.map((item, i) => (
            <li key={i} className="border-l-2 border-panelEdge pl-3">
              {typeof item === "string" ? item : (
                <div>
                  <div className="font-medium">{item.action}</div>
                  <div className="text-mute text-xs mt-0.5">{item.rationale} · {item.priority} priority · {item.timeframe}</div>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function AIInsights() {
  const { data, isLoading } = useDashboard("insights");
  const qc = useQueryClient();
  const run = useMutation({
    mutationFn: () => api.post("/analysis/run", {}),
    onSuccess: () => setTimeout(() => qc.invalidateQueries(), 4000),
  });

  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};
  const greenFlags: string[] = (p.green_flags ?? []).filter(Boolean);
  const redFlags: string[] = (p.red_flags ?? []).filter(Boolean);
  const criticalInsights: string[] = (p.critical_insights ?? []).filter(Boolean);

  return (
    <div className="space-y-4">
      <header className="flex items-center justify-between">
        <h1 className="text-xl font-semibold tracking-tight">AI Insights</h1>
        <button onClick={() => run.mutate()} disabled={run.isPending}
          className="rounded bg-amber text-ink text-sm font-semibold px-4 py-2 hover:brightness-110 disabled:opacity-60">
          {run.isPending ? "Running analysis…" : "Run analysis"}
        </button>
      </header>

      <div className="grid md:grid-cols-3 gap-4">
        <List title="Top 3 Green Flags" icon={CircleCheck} items={greenFlags} tone="text-up" />
        <List title="Top 3 Red Flags" icon={CircleX} items={redFlags} tone="text-down" />
        <List title="5 Critical Business Insights" icon={Sparkles} items={criticalInsights} tone="text-amber" />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <List title="Top Opportunities" icon={Target} items={p.top_opportunities ?? []} tone="text-up" />
        <List title="Top Risks" icon={ShieldAlert} items={p.top_risks ?? []} tone="text-down" />
        <List title="Recommended Actions" icon={Lightbulb} items={p.recommendations ?? []} tone="text-amber" />
      </div>
    </div>
  );
}
