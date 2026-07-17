import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Download, FileText } from "lucide-react";
import api from "../services/api";
import { useDocuments } from "../hooks/useDashboard";
import Skeleton from "../components/ui/Skeleton";
import type { DocumentItem } from "../types";

const STATUS_TONE: Record<string, string> = {
  embedded: "text-up", analyzed: "text-up", processing: "text-amber",
  uploaded: "text-mute", failed: "text-down",
};

export default function DocumentExplorer() {
  const { data: docs, isLoading } = useDocuments();
  const [selected, setSelected] = useState<DocumentItem | null>(null);
  const [search, setSearch] = useState("");

  const { data: chunks } = useQuery({
    queryKey: ["chunks", selected?.id],
    enabled: !!selected,
    queryFn: async () => (await api.get(`/documents/${selected!.id}/chunks`)).data as any[],
  });

  const filtered = (docs ?? []).filter((d) =>
    d.filename.toLowerCase().includes(search.toLowerCase()));

  const download = async (path: string, name: string) => {
    const resp = await api.get(path, { responseType: "blob" });
    const url = URL.createObjectURL(resp.data);
    const a = Object.assign(document.createElement("a"), { href: url, download: name });
    a.click(); URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      <header className="flex items-center justify-between gap-3">
        <h1 className="text-xl font-semibold tracking-tight">Document Explorer</h1>
        <div className="flex gap-2">
          <button onClick={() => download("/export/pdf", "executive-report.pdf")}
            className="flex items-center gap-1.5 text-sm border border-panelEdge rounded px-3 py-1.5 hover:border-amber">
            <Download size={14} /> Executive PDF
          </button>
          <button onClick={() => download("/export/excel", "financial-metrics.xlsx")}
            className="flex items-center gap-1.5 text-sm border border-panelEdge rounded px-3 py-1.5 hover:border-amber">
            <Download size={14} /> Metrics Excel
          </button>
        </div>
      </header>

      <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search documents…"
        className="w-full max-w-sm rounded bg-panel border border-panelEdge px-3 py-2 text-sm focus:border-amber outline-none" />

      {isLoading ? <Skeleton className="h-48" /> : (
        <div className="grid lg:grid-cols-2 gap-4">
          <div className="panel divide-y divide-panelEdge overflow-hidden">
            {filtered.length === 0 && <p className="p-4 text-sm text-mute">No documents yet. Upload reports to begin.</p>}
            {filtered.map((d) => (
              <button key={d.id} onClick={() => setSelected(d)}
                className={`w-full text-left px-4 py-3 flex items-center gap-3 hover:bg-ink/40 ${selected?.id === d.id ? "bg-ink/40" : ""}`}>
                <FileText size={16} className="text-mute shrink-0" />
                <div className="min-w-0 flex-1">
                  <div className="text-sm truncate">{d.filename}</div>
                  <div className="text-[11px] text-mute font-mono">
                    {d.doc_type} · {d.fiscal_period || "no period"} · v{d.version} · {(d.size_bytes / 1024).toFixed(0)} KB
                  </div>
                </div>
                <span className={`text-[11px] font-mono uppercase ${STATUS_TONE[d.status] ?? "text-mute"}`}>{d.status}</span>
              </button>
            ))}
          </div>

          <div className="panel p-4 max-h-[70vh] overflow-auto">
            <h3 className="text-xs uppercase tracking-widest text-mute mb-3">
              {selected ? `Extracted content — ${selected.filename}` : "Select a document"}
            </h3>
            {selected?.error && <p className="text-down text-sm mb-2">Processing error: {selected.error}</p>}
            {(chunks ?? []).map((c) => (
              <div key={c.id} className="mb-3 border border-panelEdge rounded p-3">
                <div className="text-[10px] font-mono text-mute mb-1">
                  chunk {c.chunk_index} · page {c.page_number} · {c.content_type}
                </div>
                <pre className="text-xs whitespace-pre-wrap font-mono text-slate-300">{c.content.slice(0, 1200)}</pre>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
