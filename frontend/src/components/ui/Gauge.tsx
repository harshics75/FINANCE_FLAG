export default function Gauge({ value, label }: { value: number | null | undefined; label: string }) {
  const v = Math.max(0, Math.min(100, value ?? 0));
  const color = v >= 70 ? "#3EE6A8" : v >= 40 ? "#FFB347" : "#FF7A93";
  const angle = (v / 100) * 180;
  const gradId = `gauge-glow-${label.replace(/\s+/g, "")}`;
  return (
    <div className="flex flex-col items-center gap-1">
      <svg viewBox="0 0 100 55" className="w-40" style={{ overflow: "visible" }}>
        <defs>
          <filter id={gradId} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2.2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <path d="M10 50 A40 40 0 0 1 90 50" fill="none" stroke="rgba(146,160,255,.13)" strokeWidth="8" strokeLinecap="round" />
        <path d="M10 50 A40 40 0 0 1 90 50" fill="none" stroke={color} strokeWidth="8" strokeLinecap="round"
          filter={`url(#${gradId})`}
          strokeDasharray={`${(angle / 180) * 125.6} 200`} />
        <text x="50" y="46" textAnchor="middle" fontSize="16" fontFamily="IBM Plex Mono" fontWeight={600} fill={color}>
          {value == null ? "—" : Math.round(v)}
        </text>
      </svg>
      <span className="text-[11px] uppercase tracking-widest text-mute">{label}</span>
    </div>
  );
}
