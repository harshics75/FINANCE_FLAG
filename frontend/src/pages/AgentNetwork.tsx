import {
  Activity, Check, FileSearch, Landmark, Lightbulb, ListChecks, Radar, Search, ShieldCheck, Sparkles,
} from "lucide-react";
import { useAnalysisRun } from "../contexts/AnalysisRunContext";
import { useRunResults } from "../hooks/useDashboard";
import ConfidenceRing from "../components/ui/ConfidenceRing";

const NODES: { id: string; label: string; icon: any; isAgent: boolean }[] = [
  { id: "retrieve_context", label: "Retrieve Context", icon: FileSearch, isAgent: false },
  { id: "financial_analyst", label: "Financial Analyst", icon: Search, isAgent: true },
  { id: "risk_detection", label: "Risk Agent", icon: ShieldCheck, isAgent: true },
  { id: "market_comparison", label: "Market Comparison", icon: Radar, isAgent: true },
  { id: "executive_summary", label: "Executive Summary", icon: Landmark, isAgent: true },
  { id: "recommendation", label: "Recommendation Agent", icon: Lightbulb, isAgent: true },
  { id: "retrieve_mis_context", label: "Retrieve MIS Context", icon: FileSearch, isAgent: false },
  { id: "operational_highlights", label: "Operational Highlights", icon: ListChecks, isAgent: true },
];

export default function AgentNetwork() {
  const { runId, progress, isRunning, startRun } = useAnalysisRun();
  const done = progress?.status === "done";
  const { data: results } = useRunResults(runId, done);

  const resultByAgent = new Map((results ?? []).map((r) => [r.agent, r.result]));
  const completed = new Set(progress?.completed ?? []);
  const currentIdx = progress ? NODES.findIndex((n) => !completed.has(n.id)) : -1;

  return (
    <div className="space-y-6 animate-rise">
      <header className="flex items-center justify-between">
        <div>
          <span className="eyebrow mb-3"><Activity size={11} /> Live pipeline execution</span>
          <h1 className="text-2xl font-semibold tracking-tight mt-2">Agent Network</h1>
          <p className="text-sm text-mute mt-1">
            {runId ? "Real status from the running pipeline — not simulated." : "Run an analysis to watch the 8-node pipeline execute live."}
          </p>
        </div>
        <button onClick={() => startRun()} disabled={isRunning}
          className="rounded-lg bg-grad text-ink text-sm font-semibold px-4 py-2.5 hover:brightness-110 disabled:opacity-60 transition-all">
          {isRunning ? "Running…" : "Run analysis"}
        </button>
      </header>

      <div className="space-y-2">
        {NODES.map((node, i) => {
          const isDone = completed.has(node.id);
          const isCurrent = i === currentIdx && isRunning;
          const state = isDone ? "done" : isCurrent ? "executing" : "pending";
          const tone = state === "done" ? "#3EE6A8" : state === "executing" ? "#33D6FF" : "#5A6284";
          const result = resultByAgent.get(node.id);
          const confidence = node.isAgent ? result?.confidence : undefined;
          const Icon = node.icon;

          return (
            <div key={node.id} className="relative flex items-stretch gap-4">
              {i < NODES.length - 1 && (
                <div className="absolute left-[19px] top-10 bottom-0 w-px"
                  style={{ background: isDone ? "#3EE6A8" : "rgba(146,160,255,.13)" }} />
              )}
              <div className="w-10 h-10 rounded-full grid place-items-center shrink-0 z-10"
                style={{ background: `${tone}22`, border: `1.5px solid ${tone}`, boxShadow: state === "executing" ? `0 0 16px ${tone}80` : "none" }}>
                {state === "done" ? <Check size={16} style={{ color: tone }} /> : <Icon size={15} style={{ color: tone }} className={state === "executing" ? "animate-pulse" : ""} />}
              </div>
              <div className="panel flex-1 p-3.5 flex items-center justify-between mb-2">
                <div>
                  <div className="text-sm font-medium">{node.label}</div>
                  <div className="text-[11px] font-mono uppercase tracking-wide" style={{ color: tone }}>
                    {state === "done" ? "Completed" : state === "executing" ? "Executing…" : node.isAgent ? "Pending" : "Standing by"}
                  </div>
                </div>
                {confidence != null && <ConfidenceRing value={confidence} tone={tone} />}
              </div>
            </div>
          );
        })}
      </div>

      {done && (
        <div className="panel p-4 flex items-center gap-2 text-sm">
          <Sparkles size={14} className="text-cyan" />
          <span>Pipeline complete — results are live on Executive Overview, AI Insights, and every other dashboard page.</span>
        </div>
      )}
    </div>
  );
}
