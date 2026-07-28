import { AlertCircle, CircleDot, FlaskConical, Lock } from "lucide-react";
import type { DataStatus } from "../../types/market";

const CONFIG: Record<DataStatus, { label: string; icon: any; className: string }> = {
  live: { label: "Live", icon: CircleDot, className: "text-up border-up/30 bg-up/10" },
  demo: { label: "Demo Data", icon: FlaskConical, className: "text-amber border-amber/30 bg-amber/10" },
  not_configured: { label: "Future Integration", icon: Lock, className: "text-mute border-panelEdge bg-white/5" },
  unavailable: { label: "Unavailable", icon: AlertCircle, className: "text-down border-down/30 bg-down/10" },
};

export default function StatusBadge({ status }: { status: DataStatus }) {
  const { label, icon: Icon, className } = CONFIG[status] ?? CONFIG.not_configured;
  return (
    <span className={`inline-flex items-center gap-1 text-[9px] font-mono uppercase tracking-wide border rounded-full px-2 py-0.5 ${className}`}>
      <Icon size={9} /> {label}
    </span>
  );
}
