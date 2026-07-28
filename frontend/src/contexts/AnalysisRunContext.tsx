import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import api from "../services/api";
import { useAnalysisProgress, type AnalysisProgress } from "../hooks/useDashboard";

interface AnalysisRunState {
  runId: string | null;
  progress: AnalysisProgress | undefined;
  isRunning: boolean;
  startRun: () => Promise<void>;
}

const AnalysisRunContext = createContext<AnalysisRunState>(null as unknown as AnalysisRunState);

export function AnalysisRunProvider({ children }: { children: ReactNode }) {
  const [runId, setRunId] = useState<string | null>(null);
  const qc = useQueryClient();
  const { data: progress } = useAnalysisProgress(runId);
  const settledRunRef = useRef<string | null>(null);

  const isRunning = !!runId && progress?.status !== "done" && progress?.status !== "failed";

  const startRun = async () => {
    const { data } = await api.post("/analysis/run", {});
    settledRunRef.current = null;
    setRunId(data.run_id);
  };

  // Once a run finishes, refresh every dashboard page so the new data shows up —
  // exactly once per run, not on every re-render.
  useEffect(() => {
    if (!runId || settledRunRef.current === runId) return;
    if (progress?.status === "done") {
      settledRunRef.current = runId;
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    } else if (progress?.status === "failed") {
      settledRunRef.current = runId;
    }
  }, [runId, progress?.status, qc]);

  return (
    <AnalysisRunContext.Provider value={{ runId, progress, isRunning, startRun }}>
      {children}
    </AnalysisRunContext.Provider>
  );
}

export const useAnalysisRun = () => useContext(AnalysisRunContext);
