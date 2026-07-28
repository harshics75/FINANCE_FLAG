export default function Sparkline({ points, tone }: { points: number[]; tone: string }) {
  if (points.length < 2) {
    return <div className="h-8 flex items-center text-[10px] text-faint">Collecting history…</div>;
  }
  const w = 120, h = 32, pad = 2;
  const min = Math.min(...points), max = Math.max(...points);
  const range = max - min || 1;
  const step = (w - pad * 2) / (points.length - 1);
  const d = points
    .map((p, i) => `${i === 0 ? "M" : "L"}${pad + i * step},${h - pad - ((p - min) / range) * (h - pad * 2)}`)
    .join(" ");
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} className="overflow-visible">
      <path d={d} fill="none" stroke={tone} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
