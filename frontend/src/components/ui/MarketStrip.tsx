import { TrendingDown, TrendingUp } from "lucide-react";
import { useMarketData } from "../../hooks/useDashboard";

function Change({ pct }: { pct: number | null | undefined }) {
  if (pct === null || pct === undefined) return null;
  const up = pct >= 0;
  return (
    <span className={`flex items-center gap-0.5 text-xs font-mono ${up ? "text-down" : "text-up"}`}>
      {up ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
      {up ? "+" : ""}{pct.toFixed(1)}%
    </span>
  );
}

export default function MarketStrip() {
  const { data } = useMarketData();
  if (!data || Object.keys(data).length === 0) return null;

  const items = [
    data.usd_inr && { label: "USD / INR", value: data.usd_inr.rate.toFixed(2), change: null },
    data.copper && {
      label: "Copper", value: `$${data.copper.value.toLocaleString()}/t`, change: data.copper.month_change_pct,
    },
    data.aluminum && {
      label: "Aluminum", value: `$${data.aluminum.value.toLocaleString()}/t`, change: data.aluminum.month_change_pct,
    },
  ].filter(Boolean) as { label: string; value: string; change: number | null }[];

  if (items.length === 0) return null;

  return (
    <div className="panel px-4 py-2.5 flex flex-wrap items-center gap-x-6 gap-y-1.5">
      <span className="text-[10px] uppercase tracking-widest text-mute">Live Market</span>
      {items.map((it) => (
        <div key={it.label} className="flex items-center gap-2">
          <span className="text-xs text-mute">{it.label}</span>
          <span className="figure text-sm">{it.value}</span>
          <Change pct={it.change} />
        </div>
      ))}
    </div>
  );
}
