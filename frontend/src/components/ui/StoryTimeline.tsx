export interface StoryStep { label: string; text: string; tone?: string; }

/** A narrative timeline built entirely from real, already-computed text — each
 * step must be sourced from actual agent output/data, never invented copy. */
export default function StoryTimeline({ steps }: { steps: StoryStep[] }) {
  if (steps.length === 0) return null;
  return (
    <div className="space-y-0">
      {steps.map((s, i) => (
        <div key={i} className="relative flex gap-4 pb-6 last:pb-0 animate-rise" style={{ animationDelay: `${i * 0.08}s` }}>
          {i < steps.length - 1 && (
            <div className="absolute left-[9px] top-6 bottom-0 w-px" style={{ background: "rgba(146,160,255,.15)" }} />
          )}
          <span className="w-[19px] h-[19px] rounded-full shrink-0 mt-0.5 grid place-items-center"
            style={{ background: `${s.tone ?? "#33D6FF"}22`, border: `1.5px solid ${s.tone ?? "#33D6FF"}` }}>
            <span className="w-1.5 h-1.5 rounded-full" style={{ background: s.tone ?? "#33D6FF" }} />
          </span>
          <div className="min-w-0 flex-1">
            <div className="text-[11px] uppercase tracking-widest font-mono" style={{ color: s.tone ?? "#33D6FF" }}>{s.label}</div>
            <p className="text-sm text-slate-200 mt-1 leading-relaxed">{s.text}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
