import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Trash2, UploadCloud } from "lucide-react";
import api from "../services/api";
import { useDocuments } from "../hooks/useDashboard";

export default function Upload() {
  const [fiscalPeriod, setFiscalPeriod] = useState("");
  const [progress, setProgress] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const qc = useQueryClient();
  const { data: docs } = useDocuments();

  const upload = async (files: FileList | null) => {
    console.log("[upload] triggered, files:", files?.length, "fiscalPeriod:", JSON.stringify(fiscalPeriod));
    if (!files?.length) {
      console.log("[upload] no files, aborting");
      return;
    }
    if (!fiscalPeriod.trim()) {
      setIsError(true);
      setMessage("Enter a fiscal period before uploading — without it, extracted figures can't be saved as usable metrics.");
      return;
    }
    setIsError(false);
    setMessage("");
    for (const file of Array.from(files)) {
      const form = new FormData();
      form.append("file", file);
      form.append("fiscal_period", fiscalPeriod);
      try {
        console.log("[upload] POSTing", file.name, file.size, "bytes");
        const res = await api.post("/documents/upload", form, {
          onUploadProgress: (e) => setProgress(e.total ? Math.round((e.loaded / e.total) * 100) : null),
        });
        console.log("[upload] success", res.status, res.data);
        setIsError(false);
        setMessage(`Uploaded ${file.name} — processing started.`);
      } catch (err: any) {
        console.error("[upload] failed", err);
        setIsError(true);
        const detail = err?.response?.data?.detail ?? err?.message ?? "unknown error";
        setMessage(`Upload failed for ${file.name}: ${detail} (${err?.response?.status ?? "no response"})`);
      }
    }
    setProgress(null);
    qc.invalidateQueries({ queryKey: ["documents"] });
  };

  const remove = async (id: string, filename: string) => {
    if (!confirm(`Delete "${filename}"? This also removes its extracted chunks and metrics.`)) return;
    try {
      await api.delete(`/documents/${id}`);
      qc.invalidateQueries({ queryKey: ["documents"] });
    } catch {
      setMessage(`Failed to delete ${filename}.`);
    }
  };

  return (
    <div className="space-y-4 max-w-2xl">
      <h1 className="text-xl font-semibold tracking-tight">Upload Financial Reports</h1>
      <div className="panel p-5 space-y-4">
        <label className="block text-sm">
          <span className="text-mute text-xs uppercase tracking-widest">Fiscal period (required, e.g. FY2025-26)</span>
          <input value={fiscalPeriod} onChange={(e) => setFiscalPeriod(e.target.value)} placeholder="FY2025-26"
            className="mt-1 w-full rounded bg-ink border border-panelEdge px-3 py-2 text-sm focus:border-amber outline-none" />
        </label>
        <div className="relative border-2 border-dashed border-panelEdge rounded-lg p-10 text-center hover:border-amber"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => { e.preventDefault(); upload(e.dataTransfer.files); }}>
          <UploadCloud className="mx-auto text-mute mb-2" size={28} />
          <span className="text-sm text-mute">Drop PDF or Excel files here, or click to browse (max 50 MB)</span>
          <input type="file" multiple accept=".pdf,.xlsx,.xls"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            onChange={(e) => { upload(e.target.files); e.target.value = ""; }} />
        </div>
        {progress !== null && (
          <div className="h-1.5 bg-panelEdge rounded overflow-hidden">
            <div className="h-full bg-amber transition-all" style={{ width: `${progress}%` }} />
          </div>
        )}
        {message && <p className={`text-sm ${isError ? "text-down" : "text-mute"}`}>{message}</p>}
      </div>
      <div className="panel p-4">
        <h3 className="text-xs uppercase tracking-widest text-mute mb-3">Recent uploads</h3>
        <ul className="space-y-1.5 text-sm">
          {(docs ?? []).slice(0, 8).map((d) => (
            <li key={d.id} className="flex items-center justify-between gap-2">
              <span className="truncate">{d.filename}</span>
              <span className="flex items-center gap-2 shrink-0">
                <span className="font-mono text-[11px] text-mute uppercase">{d.status}</span>
                <button onClick={() => remove(d.id, d.filename)} aria-label={`Delete ${d.filename}`}
                  className="text-mute hover:text-down transition-colors p-1">
                  <Trash2 size={13} />
                </button>
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
