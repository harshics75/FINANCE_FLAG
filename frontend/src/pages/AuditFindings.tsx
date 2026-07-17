import { ShieldAlert } from "lucide-react";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import { useDashboard } from "../hooks/useDashboard";

const SEV_TONE: Record<string, string> = {
  critical: "border-down text-down", high: "border-down text-down",
  medium: "border-amber text-amber", low: "border-up text-up",
};

export default function AuditFindings() {
  const { data, isLoading } = useDashboard("audit");
  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};
  const risks: any[] = p.risks ?? [];
  const obs: string[] = p.audit_observations ?? [];

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold tracking-tight">Audit Findings</h1>
      <div className="grid md:grid-cols-2 gap-4">
        <div className="panel p-4">
          <h3 className="flex items-center gap-2 text-xs uppercase tracking-widest text-down mb-3">
            <ShieldAlert size={14} /> Control & Compliance Risks
          </h3>
          {risks.length === 0 ? <p className="text-sm text-mute">No compliance or audit-category risks detected yet.</p> : (
            <ul className="space-y-3">
              {risks.map((r, i) => (
                <li key={i} className={`border-l-2 pl-3 ${SEV_TONE[r.severity] ?? "border-panelEdge"}`}>
                  <div className="text-sm font-medium">{r.title}</div>
                  <div className="text-xs text-mute mt-0.5">{r.evidence}</div>
                  <div className="text-[10px] font-mono uppercase mt-1">{r.severity} · {r.category}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="panel p-4">
          <h3 className="text-xs uppercase tracking-widest text-mute mb-3">Audit Observations</h3>
          {obs.length === 0 ? <p className="text-sm text-mute">Upload an audit report and run analysis.</p> : (
            <ul className="space-y-2 text-sm">
              {obs.map((o, i) => <li key={i} className="border-l-2 border-panelEdge pl-3">{o}</li>)}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
