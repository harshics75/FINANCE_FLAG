import { Check, Sparkles } from "lucide-react";
import { useAnalysisRun } from "../../contexts/AnalysisRunContext";

const DEFAULT_LABELS: Record<string, string> = {
  retrieve_context: "Reading financial statements…",
  financial_analyst: "Running ratio analysis…",
  risk_detection: "Detecting risks…",
  market_comparison: "Comparing industry & market signals…",
  executive_summary: "Generating executive summary…",
  recommendation: "Generating recommendations…",
  retrieve_mis_context: "Reading monthly MIS report…",
  operational_highlights: "Extracting operational highlights…",
};

/** A real, live view into the actual 8-node pipeline — reuses the same
 * progress data as the Agent Network page. Idle state when nothing is running,
 * never a fake fixed-timing animation. */
export default function LiveThinkingPanel({ labels = DEFAULT_LABELS, title = "Live AI Thinking" }: {
  labels?: Record<string, string>; title?: string;
}) {
  const { progress, isRunning } = useAnalysisRun();

  if (!isRunning || !progress) {
    return (
      <div className="panel p-4">
        <h3 className="flex items-center gap-2 text-xs uppercase tracking-widest text-mute mb-3">
          <Sparkles size={12} className="text-cyan" /> {title}
        </h3>
        <p className="text-sm text-mute">Idle — click "Run analysis" to watch this update live.</p>
      </div>
    );
  }

  return (
    <div className="panel p-4">
      <h3 className="flex items-center gap-2 text-xs uppercase tracking-widest text-cyan mb-3">
        <span className="pulse-dot" /> {title}
      </h3>
      <div className="space-y-2.5">
        {progress.nodes.map((node) => {
          const done = progress.completed.includes(node);
          const current = !done && progress.nodes.find((n) => !progress.completed.includes(n)) === node;
          return (
            <div key={node} className="flex items-center gap-2.5 text-xs">
              <span className={`w-4 h-4 rounded-full grid place-items-center shrink-0 border ${
                done ? "bg-up/20 border-up text-up" : current ? "border-cyan text-cyan animate-pulse" : "border-panelEdge text-faint"}`}>
                {done && <Check size={10} />}
              </span>
              <span className={done ? "text-mute line-through" : current ? "text-cyan font-medium" : "text-faint"}>
                {labels[node] ?? node}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
