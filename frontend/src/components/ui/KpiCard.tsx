import { motion } from "framer-motion";
import { TrendingDown, TrendingUp } from "lucide-react";

export function formatNum(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  const abs = Math.abs(v);
  if (abs >= 1e7) return (v / 1e7).toFixed(2) + " Cr";
  if (abs >= 1e5) return (v / 1e5).toFixed(2) + " L";
  if (abs >= 1e3) return (v / 1e3).toFixed(1) + "K";
  return v.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

export default function KpiCard({ label, value, suffix, delta }: {
  label: string; value: number | null | undefined; suffix?: string; delta?: number | null;
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
      className="panel p-4 flex flex-col gap-1">
      <span className="text-[11px] uppercase tracking-widest text-mute">{label}</span>
      <span className="figure text-2xl font-semibold">{formatNum(value)}{suffix ?? ""}</span>
      {delta !== undefined && delta !== null && (
        <span className={`flex items-center gap-1 text-xs font-mono ${delta >= 0 ? "text-up" : "text-down"}`}>
          {delta >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
          {delta >= 0 ? "+" : ""}{delta.toFixed(1)}%
        </span>
      )}
    </motion.div>
  );
}
