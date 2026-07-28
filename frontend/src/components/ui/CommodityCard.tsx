import { TrendingDown, TrendingUp } from "lucide-react";
import { useSeriesHistory } from "../../hooks/useDashboard";
import StatusBadge from "./StatusBadge";
import Sparkline from "./Sparkline";
import type { BusinessImpact, CommoditySeries } from "../../types/market";

const RISK_TONE: Record<string, string> = {
  low: "text-up border-up/30", medium: "text-amber border-amber/30", high: "text-down border-down/30",
};

export default function CommodityCard({ seriesKey, label, data, impact, tone }: {
  seriesKey: string; label: string; data: CommoditySeries; impact?: BusinessImpact; tone: string;
}) {
  const { data: history } = useSeriesHistory(seriesKey);
  const live = data.status === "live";
  const value = data.value ?? data.rate;
  const pct = data.month_change_pct;
  const rising = (pct ?? 0) >= 0;

  return (
    <div className="panel panel-interactive relative p-4 overflow-hidden animate-rise">
      <span className="absolute inset-x-0 top-0 h-px" style={{ background: `linear-gradient(90deg, transparent, ${tone}, transparent)`, opacity: .6 }} />
      <div className="flex items-start justify-between gap-2">
        <span className="text-[11px] uppercase tracking-widest text-mute">{label}</span>
        <StatusBadge status={data.status} />
      </div>

      {live ? (
        <>
          <div className="figure text-2xl font-semibold mt-2" style={{ color: tone }}>
            {value?.toLocaleString()} <span className="text-xs text-mute font-sans">{data.unit}</span>
          </div>
          <div className="flex items-center justify-between mt-2">
            {pct != null ? (
              <span className={`flex items-center gap-1 text-xs font-mono ${rising ? "text-down" : "text-up"}`}>
                {rising ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                {rising ? "+" : ""}{pct.toFixed(1)}% MoM
              </span>
            ) : <span />}
            <Sparkline points={(history ?? []).map((h) => h.value)} tone={tone} />
          </div>
          {impact && (
            <div className="mt-3 pt-3 border-t border-panelEdge space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase tracking-wide text-faint">Risk</span>
                <span className={`text-[10px] font-mono uppercase border rounded px-1.5 py-0.5 ${RISK_TONE[impact.risk_level]}`}>
                  {impact.risk_level}
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{impact.business_impact[0]}</p>
              <p className="text-[10px] text-faint">{impact.affected_departments.join(" · ")}</p>
            </div>
          )}
        </>
      ) : (
        <div className="mt-3 text-xs text-faint leading-relaxed">
          {data.status === "unavailable"
            ? "Live call failed just now — will retry on next refresh."
            : data.future_integration ?? "Requires a licensed data feed."}
        </div>
      )}
      <p className="text-[9px] text-faint mt-3">{data.source}</p>
    </div>
  );
}
