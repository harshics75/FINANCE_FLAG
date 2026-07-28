export default function ConfidenceRing({ value, tone = "#33D6FF", size = 34 }: {
  value: number | null | undefined; tone?: string; size?: number;
}) {
  if (value === null || value === undefined) return null;
  const v = Math.max(0, Math.min(100, value));
  const r = 14, c = 2 * Math.PI * r;
  return (
    <div className="relative shrink-0" style={{ width: size, height: size }} title={`Confidence: ${Math.round(v)}%`}>
      <svg width={size} height={size} viewBox="0 0 34 34" style={{ transform: "rotate(-90deg)" }}>
        <circle cx="17" cy="17" r={r} fill="none" stroke="rgba(255,255,255,.08)" strokeWidth="3" />
        <circle cx="17" cy="17" r={r} fill="none" stroke={tone} strokeWidth="3" strokeLinecap="round"
          strokeDasharray={c} strokeDashoffset={c - (c * v) / 100} />
      </svg>
      <div className="absolute inset-0 grid place-items-center font-mono" style={{ fontSize: size * 0.28, color: tone }}>
        {Math.round(v)}
      </div>
    </div>
  );
}
