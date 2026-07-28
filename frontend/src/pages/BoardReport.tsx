import { Download, FileSpreadsheet, FileText, Presentation, Sparkles } from "lucide-react";
import api from "../services/api";
import TypingReveal from "../components/ui/TypingReveal";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import { useDashboard } from "../hooks/useDashboard";

function DownloadCard({ icon: Icon, title, desc, path, filename }: {
  icon: any; title: string; desc: string; path: string; filename: string;
}) {
  const download = async () => {
    const resp = await api.get(path, { responseType: "blob" });
    const url = URL.createObjectURL(resp.data);
    const a = Object.assign(document.createElement("a"), { href: url, download: filename });
    a.click();
    URL.revokeObjectURL(url);
  };
  return (
    <button onClick={download} className="panel panel-interactive p-4 text-left flex items-start gap-3">
      <div className="w-9 h-9 rounded-[10px] grid place-items-center shrink-0 bg-cyan/10 text-cyan border border-cyan/25">
        <Icon size={16} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="text-sm font-medium flex items-center gap-1.5">{title} <Download size={12} className="text-mute" /></div>
        <div className="text-xs text-mute mt-0.5">{desc}</div>
      </div>
    </button>
  );
}

export default function BoardReport() {
  const { data, isLoading } = useDashboard("executive");
  const { data: insightsData } = useDashboard("insights");
  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};
  const insights = insightsData?.payload ?? {};

  return (
    <div className="space-y-6 animate-rise">
      <header>
        <span className="eyebrow mb-3"><Sparkles size={11} /> Board-ready, built from real analysis data</span>
        <h1 className="text-2xl font-semibold tracking-tight mt-2">Board Report</h1>
        <p className="text-sm text-mute mt-1">Every export below pulls from the same live dashboard data — nothing is fabricated at export time.</p>
      </header>

      <div className="grid md:grid-cols-3 gap-3">
        <DownloadCard icon={FileText} title="Executive PDF" desc="Headline, KPIs, highlights, risks, recommendations"
          path="/export/pdf" filename="executive-report.pdf" />
        <DownloadCard icon={FileSpreadsheet} title="Metrics Excel" desc="Every financial metric, by fiscal period"
          path="/export/excel" filename="financial-metrics.xlsx" />
        <DownloadCard icon={Presentation} title="Board PowerPoint" desc="5-slide deck: summary, health, flags, actions"
          path="/export/pptx" filename="board-report.pptx" />
      </div>

      {p.summary && (
        <div className="panel p-5">
          <h3 className="flex items-center gap-2 text-xs uppercase tracking-widest text-mute mb-3">
            <Sparkles size={12} className="text-cyan" /> Preview — Executive Summary
          </h3>
          <TypingReveal text={p.summary} />
        </div>
      )}

      {(insights.critical_insights ?? []).length > 0 && (
        <div className="panel p-5">
          <h3 className="text-xs uppercase tracking-widest text-mute mb-3">Preview — Critical Business Insights</h3>
          <ul className="space-y-2 text-sm">
            {insights.critical_insights.map((c: string, i: number) => (
              <li key={i} className="border-l-2 border-panelEdge pl-3">{c}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
