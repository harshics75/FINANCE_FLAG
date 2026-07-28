import { Sparkles } from "lucide-react";
import ConfidenceRing from "./ConfidenceRing";

export default function IntelligenceCard({ icon: Icon, tone, title, value, explanation, reason, impact, forecast, confidence, onDeepDive }: {
  icon: any; tone: string; title: string; value: string;
  explanation?: string; reason?: string; impact?: string; forecast?: string | null;
  confidence?: number | null; onDeepDive?: () => void;
}) {
  return (
    <div className="panel panel-interactive relative p-4 overflow-hidden animate-rise">
      <span className="absolute inset-x-0 top-0 h-px" style={{ background: `linear-gradient(90deg, transparent, ${tone}, transparent)`, opacity: .6 }} />
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-[10px] grid place-items-center shrink-0"
            style={{ background: `${tone}22`, color: tone, border: `1px solid ${tone}4d` }}>
            <Icon size={15} />
          </div>
          <span className="text-[11px] uppercase tracking-widest text-mute">{title}</span>
        </div>
        {confidence != null && <ConfidenceRing value={confidence} tone={tone} size={30} />}
      </div>

      <div className="figure text-2xl font-semibold mt-3" style={{ color: tone }}>{value}</div>

      <div className="mt-3 space-y-1.5 text-xs">
        {explanation && <p className="text-slate-300 leading-relaxed">{explanation}</p>}
        {reason && (
          <div className="flex gap-2">
            <span className="text-faint uppercase tracking-wide text-[10px] w-14 shrink-0 pt-0.5">Reason</span>
            <span className="text-slate-400">{reason}</span>
          </div>
        )}
        {impact && (
          <div className="flex gap-2">
            <span className="text-faint uppercase tracking-wide text-[10px] w-14 shrink-0 pt-0.5">Impact</span>
            <span className="text-slate-400">{impact}</span>
          </div>
        )}
        {forecast && (
          <div className="flex gap-2">
            <span className="text-faint uppercase tracking-wide text-[10px] w-14 shrink-0 pt-0.5">Forecast</span>
            <span className="font-mono" style={{ color: tone }}>{forecast}</span>
          </div>
        )}
      </div>

      {onDeepDive && (
        <div className="mt-3 pt-3 border-t border-panelEdge">
          <button onClick={onDeepDive}
            className="flex items-center gap-1.5 text-[11px] font-semibold px-3 py-1.5 rounded-lg transition-colors"
            style={{ color: tone, background: `${tone}14`, border: `1px solid ${tone}40` }}>
            <Sparkles size={11} /> Deep Dive
          </button>
        </div>
      )}
    </div>
  );
}
