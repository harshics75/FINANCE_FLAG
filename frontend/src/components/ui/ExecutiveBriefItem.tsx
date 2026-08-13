import { AlertCircle, ArrowUpRight, CheckCircle2 } from "lucide-react";
import type { ExecutiveBriefItem as ExecutiveBriefItemType } from "../../types/market";

const TONE: Record<string, { color: string; icon: any }> = {
  red: { color: "#FF7A93", icon: AlertCircle },
  amber: { color: "#FFB347", icon: ArrowUpRight },
  green: { color: "#3EE6A8", icon: CheckCircle2 },
};

export default function ExecutiveBriefItem({ item }: { item: ExecutiveBriefItemType }) {
  const { color, icon: Icon } = TONE[item.tone] ?? TONE.amber;
  return (
    <div className="flex items-start gap-2.5 text-sm">
      <Icon size={14} className="mt-0.5 shrink-0" style={{ color }} />
      <div>
        <span className="text-slate-200">{item.headline}</span>
        {item.why_it_matters && <span className="text-mute"> — {item.why_it_matters}</span>}
        <p className="text-[10px] text-faint mt-0.5">{item.source}</p>
      </div>
    </div>
  );
}
