import { Activity, Sparkles } from "lucide-react";
import { useAnalysisRun } from "../../contexts/AnalysisRunContext";
import { useSystemInfo } from "../../hooks/useDashboard";

const NODE_LABEL: Record<string, string> = {
  retrieve_context: "Reading financial documents…",
  financial_analyst: "Analyzing financial performance…",
  risk_detection: "Detecting risks…",
  market_comparison: "Comparing market & commodity data…",
  executive_summary: "Writing executive summary…",
  recommendation: "Generating recommendations…",
  retrieve_mis_context: "Reading monthly MIS report…",
  operational_highlights: "Extracting operational highlights…",
};

export default function AIAvatarHero() {
  const { progress, isRunning, startRun } = useAnalysisRun();
  const { data: system } = useSystemInfo();

  const currentNode = isRunning
    ? progress?.nodes.find((n) => !progress.completed.includes(n))
    : undefined;
  const statusText = isRunning
    ? (currentNode ? NODE_LABEL[currentNode] ?? "Working…" : "Finishing up…")
    : "Ready — ask me anything or run a fresh analysis";

  return (
    <div className="panel p-4 flex items-center gap-4">
      <div className="relative w-11 h-11 shrink-0">
        <div className={`absolute inset-0 rounded-full bg-grad ${isRunning ? "animate-pulse" : "animate-float"}`}
          style={{ boxShadow: "0 0 24px rgba(93,140,255,.5)" }} />
        <div className="absolute inset-0 rounded-full grid place-items-center">
          <Activity size={18} className="text-ink" />
        </div>
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="pulse-dot" style={isRunning ? {} : { animation: "none", opacity: 0.5 }} />
          <span className={`text-sm font-medium truncate ${isRunning ? "text-cyan" : "text-slate-200"}`}>{statusText}</span>
        </div>
        {system && (
          <span className="text-[11px] font-mono text-faint">{system.label} · {system.chat_model}</span>
        )}
      </div>
      <button onClick={() => startRun()} disabled={isRunning}
        className="flex items-center gap-1.5 rounded-lg bg-grad text-ink text-sm font-semibold px-4 py-2.5
          hover:brightness-110 disabled:opacity-50 transition-all shrink-0">
        <Sparkles size={14} /> {isRunning ? "Analyzing…" : "Run analysis"}
      </button>
    </div>
  );
}
