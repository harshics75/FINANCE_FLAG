import { ExternalLink } from "lucide-react";
import type { MarketSignal } from "../../types/market";

const KIND_TONE: Record<string, string> = {
  material: "text-amber border-amber/30 bg-amber/10",
  sector: "text-cyan border-cyan/30 bg-cyan/10",
};

export default function MarketSignalItem({ signal }: { signal: MarketSignal }) {
  const s = signal;
  return (
    <div className="border-b border-panelEdge last:border-0 pb-3 last:pb-0">
      <a href={s.url} target="_blank" rel="noreferrer" className="flex items-start justify-between gap-3 group">
        <span className="text-sm font-medium group-hover:text-cyan transition-colors">{s.title}</span>
        <ExternalLink size={13} className="text-mute shrink-0 mt-0.5" />
      </a>
      <div className="flex items-center gap-2 mt-1.5 flex-wrap">
        <span className={`text-[9px] font-mono uppercase border rounded px-1.5 py-0.5 ${KIND_TONE[s.kind] ?? KIND_TONE.sector}`}>
          {s.sector_label}
        </span>
        <span className="text-[10px] text-mute">Relevance {s.relevance_score}/100</span>
        <span className="text-[10px] text-faint">· {s.source_name || "newsdata.io"}</span>
      </div>
    </div>
  );
}
