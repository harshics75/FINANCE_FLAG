import StatusBadge from "./StatusBadge";
import type { MarketOpportunity } from "../../types/market";

const RELEVANCE_TONE: Record<string, string> = {
  high: "text-up border-up/30 bg-up/10", medium: "text-amber border-amber/30 bg-amber/10", low: "text-mute border-panelEdge",
};

export default function OpportunityCard({ opportunity }: { opportunity: MarketOpportunity }) {
  const o = opportunity;
  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between gap-2">
        <span className="text-sm font-medium">{o.title}</span>
        <StatusBadge status={o.status} />
      </div>
      <p className="text-xs text-mute mt-1">{o.location || "Location not specified"} · {o.sector_label} · {o.stage}</p>

      <div className="flex items-center justify-between mt-3">
        <span className="figure text-lg text-up">
          {o.project_value_cr != null ? `₹${o.project_value_cr.toLocaleString()} Cr` : "Value not disclosed"}
        </span>
        <span className="text-xs text-mute">Relevance <span className="text-cyan font-mono">{o.relevance_score}</span>/100</span>
      </div>
      <p className="text-[10px] text-faint mt-1">
        Stardrive opportunity: {o.stardrive_opportunity_value_cr != null
          ? `₹${o.stardrive_opportunity_value_cr.toLocaleString()} Cr`
          : "Not yet estimated"}
      </p>

      <div className="flex items-center gap-2 mt-2 flex-wrap">
        <span className={`text-[9px] font-mono uppercase border rounded px-1.5 py-0.5 ${RELEVANCE_TONE[o.busduct_relevance] ?? RELEVANCE_TONE.low}`}>
          {o.busduct_relevance} busduct relevance
        </span>
        {o.is_emerging && (
          <span className="text-[9px] font-mono uppercase border border-violet/30 text-violet bg-violet/10 rounded px-1.5 py-0.5">
            Emerging opportunity
          </span>
        )}
      </div>
      <p className="text-[10px] text-faint mt-2">
        Demand: {o.material_demand.join(", ") || "—"} · Confidence {o.confidence}% · {o.source_name}
      </p>
    </div>
  );
}
