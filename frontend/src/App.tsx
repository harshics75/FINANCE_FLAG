import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import AppShell from "./layouts/AppShell";
import Login from "./pages/Login";
import ExecutiveOverview from "./pages/ExecutiveOverview";
import FinancialPerformance from "./pages/FinancialPerformance";
import CashFlowDashboard from "./pages/CashFlowDashboard";
import WorkingCapital from "./pages/WorkingCapital";
import AIInsights from "./pages/AIInsights";
import AgentNetwork from "./pages/AgentNetwork";
import ForecastTimeline from "./pages/ForecastTimeline";
import OperationalHighlights from "./pages/OperationalHighlights";
import MarketIntelligenceOperations from "./pages/MarketIntelligenceOperations";
import MarketIntelligenceStrategy from "./pages/MarketIntelligenceStrategy";
import DocumentExplorer from "./pages/DocumentExplorer";
import AuditFindings from "./pages/AuditFindings";
import BoardReport from "./pages/BoardReport";
import Chat from "./pages/Chat";
import Upload from "./pages/Upload";

function Protected({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen grid place-items-center text-mute text-sm">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Protected><AppShell /></Protected>}>
        <Route path="/" element={<ExecutiveOverview />} />
        <Route path="/performance" element={<FinancialPerformance />} />
        <Route path="/cash-flow" element={<CashFlowDashboard />} />
        <Route path="/working-capital" element={<WorkingCapital />} />
        <Route path="/insights" element={<AIInsights />} />
        <Route path="/agents" element={<AgentNetwork />} />
        <Route path="/forecast" element={<ForecastTimeline />} />
        <Route path="/operational" element={<OperationalHighlights />} />
        <Route path="/market" element={<MarketIntelligenceOperations />} />
        <Route path="/market/strategy" element={<MarketIntelligenceStrategy />} />
        <Route path="/documents" element={<DocumentExplorer />} />
        <Route path="/audit" element={<AuditFindings />} />
        <Route path="/board-report" element={<BoardReport />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/upload" element={<Upload />} />
      </Route>
    </Routes>
  );
}
