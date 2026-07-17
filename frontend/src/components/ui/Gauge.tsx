export default function Gauge({ value, label }: { value: number | null | undefined; label: string }) {
  const v = Math.max(0, Math.min(100, value ?? 0));
  const color = v >= 70 ? "#2DD4BF" : v >= 40 ? "#FFB020" : "#F87171";
  const angle = (v / 100) * 180;
  return (
    <div className="flex flex-col items-center gap-1">
      <svg viewBox="0 0 100 55" className="w-40">
        <path d="M10 50 A40 40 0 0 1 90 50" fill="none" stroke="#1E2A44" strokeWidth="8" strokeLinecap="round" />
        <path d="M10 50 A40 40 0 0 1 90 50" fill="none" stroke={color} strokeWidth="8" strokeLinecap="round"
          strokeDasharray={`${(angle / 180) * 125.6} 200`} />
        <text x="50" y="46" textAnchor="middle" className="fill-current" fontSize="16" fontFamily="IBM Plex Mono" fill={color}>
          {value == null ? "—" : Math.round(v)}
        </text>
      </svg>
      <span className="text-[11px] uppercase tracking-widest text-mute">{label}</span>
    </div>
  );
}
