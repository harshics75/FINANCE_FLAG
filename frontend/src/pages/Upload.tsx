import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { UploadCloud } from "lucide-react";
import api from "../services/api";
import { useDocuments } from "../hooks/useDashboard";

export default function Upload() {
  const [fiscalPeriod, setFiscalPeriod] = useState("");
  const [progress, setProgress] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const qc = useQueryClient();
  const { data: docs } = useDocuments();

  const upload = async (files: FileList | null) => {
    if (!files?.length) return;
    setMessage("");
    for (const file of Array.from(files)) {
      const form = new FormData();
      form.append("file", file);
      form.append("fiscal_period", fiscalPeriod);
      try {
        await api.post("/documents/upload", form, {
          onUploadProgress: (e) => setProgress(e.total ? Math.round((e.loaded / e.total) * 100) : null),
        });
        setMessage(`Uploaded ${file.name} — processing started.`);
      } catch (err: any) {
        setMessage(err?.response?.data?.detail ?? `Upload failed for ${file.name}.`);
      }
    }
    setProgress(null);
    qc.invalidateQueries({ queryKey: ["documents"] });
  };

  return (
    <div className="space-y-4 max-w-2xl">
      <h1 className="text-xl font-semibold tracking-tight">Upload Financial Reports</h1>
      <div className="panel p-5 space-y-4">
        <label className="block text-sm">
          <span className="text-mute text-xs uppercase tracking-widest">Fiscal period (e.g. FY2025-26)</span>
          <input value={fiscalPeriod} onChange={(e) => setFiscalPeriod(e.target.value)} placeholder="FY2025-26"
            className="mt-1 w-full rounded bg-ink border border-panelEdge px-3 py-2 text-sm focus:border-amber outline-none" />
        </label>
        <label className="block border-2 border-dashed border-panelEdge rounded-lg p-10 text-center cursor-pointer hover:border-amber"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => { e.preventDefault(); upload(e.dataTransfer.files); }}>
          <UploadCloud className="mx-auto text-mute mb-2" size={28} />
          <span className="text-sm text-mute">Drop PDF or Excel files here, or click to browse (max 50 MB)</span>
          <input type="file" multiple accept=".pdf,.xlsx,.xls" className="hidden"
            onChange={(e) => upload(e.target.files)} />
        </label>
        {progress !== null && (
          <div className="h-1.5 bg-panelEdge rounded overflow-hidden">
            <div className="h-full bg-amber transition-all" style={{ width: `${progress}%` }} />
          </div>
        )}
        {message && <p className="text-sm text-mute">{message}</p>}
      </div>
      <div className="panel p-4">
        <h3 className="text-xs uppercase tracking-widest text-mute mb-3">Recent uploads</h3>
        <ul className="space-y-1.5 text-sm">
          {(docs ?? []).slice(0, 8).map((d) => (
            <li key={d.id} className="flex justify-between">
              <span className="truncate">{d.filename}</span>
              <span className="font-mono text-[11px] text-mute uppercase">{d.status}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
