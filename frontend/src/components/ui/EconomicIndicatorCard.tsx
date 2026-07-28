import StatusBadge from "./StatusBadge";
import type { EconomicIndicator } from "../../types/market";

export default function EconomicIndicatorCard({ data, tone }: { data: EconomicIndicator; tone: string }) {
  const live = data.status === "live";
  return (
    <div className="panel p-4 relative overflow-hidden">
      <span className="absolute inset-x-0 top-0 h-px" style={{ background: `linear-gradient(90deg, transparent, ${tone}, transparent)`, opacity: .6 }} />
      <div className="flex items-start justify-between gap-2">
        <span className="text-[11px] uppercase tracking-widest text-mute">{data.name}</span>
        <StatusBadge status={data.status} />
      </div>
      {live ? (
        <>
          <div className="figure text-xl font-semibold mt-2" style={{ color: tone }}>
            {data.value}
            <span className="text-xs text-mute font-sans ml-1">{data.unit}</span>
          </div>
          <p className="text-[10px] text-faint mt-1.5">
            {data.is_forecast ? "Forecast · " : ""}As of {data.as_of} · {data.source}
          </p>
        </>
      ) : (
        <p className="text-[11px] text-faint mt-2 leading-relaxed">
          {data.status === "unavailable" ? "Live call failed — will retry." : data.future_integration ?? data.source}
        </p>
      )}
    </div>
  );
}
