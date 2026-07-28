import { Sparkles } from "lucide-react";
import ConfidenceRing from "./ConfidenceRing";

export function SectionHeader({ title, icon: Icon, tone, confidence }: {
  title: string; icon: any; tone: string; confidence?: number | null;
}) {
  return (
    <div className="flex items-center justify-between mb-3">
      <h2 className="flex items-center gap-2 text-xs uppercase tracking-widest text-mute">
        <span style={{ color: tone }}><Icon size={12} /></span> {title}
      </h2>
      {confidence != null && (
        <span className="flex items-center gap-1.5 text-[10px] font-mono text-faint">
          <ConfidenceRing value={confidence} tone={tone} size={22} /> analysis confidence
        </span>
      )}
    </div>
  );
}

export default function InsightCard({ icon: Icon, tone, title, cause, impact, tag, confidence, onExplain }: {
  icon: any; tone: string; title: string; cause?: string; impact?: string; tag?: string;
  confidence?: number | null; onExplain?: () => void;
}) {
  return (
    <div className="panel panel-interactive relative p-4 overflow-hidden animate-rise">
      <span className="absolute inset-x-0 top-0 h-px" style={{ background: `linear-gradient(90deg, transparent, ${tone}, transparent)`, opacity: .6 }} />
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-[10px] grid place-items-center shrink-0"
          style={{ background: `${tone}22`, color: tone, border: `1px solid ${tone}4d` }}>
          <Icon size={15} />
        </div>
        <h3 className="text-sm font-medium leading-snug pt-1 flex-1">{title}</h3>
        {confidence != null && <ConfidenceRing value={confidence} tone={tone} size={28} />}
      </div>
      {(cause || impact) && (
        <div className="mt-3 space-y-1.5 text-xs pl-11">
          {cause && (
            <div className="flex gap-2">
              <span className="text-faint uppercase tracking-wide text-[10px] w-12 shrink-0 pt-0.5">Why</span>
              <span className="text-slate-300">{cause}</span>
            </div>
          )}
          {impact && (
            <div className="flex gap-2">
              <span className="text-faint uppercase tracking-wide text-[10px] w-12 shrink-0 pt-0.5">Impact</span>
              <span className="font-mono" style={{ color: tone }}>{impact}</span>
            </div>
          )}
        </div>
      )}
      {(tag || onExplain) && (
        <div className="flex items-center gap-2 mt-3 pt-3 border-t border-panelEdge">
          {tag && (
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full border"
              style={{ borderColor: `${tone}4d`, color: tone }}>{tag}</span>
          )}
          {onExplain && (
            <button onClick={onExplain}
              className="ml-auto flex items-center gap-1.5 text-[11px] font-semibold px-3 py-1.5 rounded-lg transition-colors"
              style={{ color: tone, background: `${tone}14`, border: `1px solid ${tone}40` }}>
              <Sparkles size={11} /> Explain
            </button>
          )}
        </div>
      )}
    </div>
  );
}
