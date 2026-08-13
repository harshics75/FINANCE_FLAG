import type { CoreSectorIntelligence } from "../../types/market";

const RELEVANCE_TONE: Record<string, string> = {
  "very high": "text-up border-up/30 bg-up/10",
  high: "text-cyan border-cyan/30 bg-cyan/10",
  medium: "text-amber border-amber/30 bg-amber/10",
  low: "text-mute border-panelEdge",
};

export default function SectorIntelCard({ sector }: { sector: CoreSectorIntelligence }) {
  const s = sector;
  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between gap-2">
        <span className="text-sm font-medium">{s.label}</span>
        <span className={`text-[9px] font-mono uppercase border rounded px-1.5 py-0.5 shrink-0 ${RELEVANCE_TONE[s.stardrive_relevance] ?? RELEVANCE_TONE.low}`}>
          {s.stardrive_relevance} relevance
        </span>
      </div>
      <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
        <div>
          <div className="text-faint text-[10px] uppercase tracking-wide">Opportunities</div>
          <div className="font-mono text-slate-200">{s.relevant_opportunities}</div>
        </div>
        <div>
          <div className="text-faint text-[10px] uppercase tracking-wide">Potential Value</div>
          <div className="font-mono text-slate-200">
            {s.potential_project_value_cr != null ? `₹${s.potential_project_value_cr.toLocaleString()} Cr` : "—"}
          </div>
        </div>
      </div>
      <p className="text-[10px] text-faint mt-3">
        FY23-24: ₹{s.historical_enquiry_cr.toLocaleString()} Cr enquiry · ₹{s.historical_orders_cr.toLocaleString()} Cr orders · {s.historical_conversion_pct.toFixed(1)}% conversion
      </p>
    </div>
  );
}
