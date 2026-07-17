import { AlertTriangle, ClipboardList, Factory, Gavel, ListChecks } from "lucide-react";
import { DashboardSkeleton } from "../components/ui/Skeleton";
import { useDashboard } from "../hooks/useDashboard";

function Card({ title, icon: Icon, children }: { title: string; icon: any; children: React.ReactNode }) {
  return (
    <div className="panel p-4">
      <h3 className="flex items-center gap-2 text-xs uppercase tracking-widest text-mute mb-3">
        <Icon size={14} /> {title}
      </h3>
      {children}
    </div>
  );
}

function TextBlock({ value }: { value: string }) {
  return value ? (
    <p className="text-sm leading-relaxed">{value}</p>
  ) : (
    <p className="text-sm text-mute">Not mentioned in the latest monthly MIS report.</p>
  );
}

function ListBlock({ items }: { items: string[] }) {
  return items.length === 0 ? (
    <p className="text-sm text-mute">None reported.</p>
  ) : (
    <ul className="space-y-2 text-sm">
      {items.map((item, i) => (
        <li key={i} className="border-l-2 border-panelEdge pl-3">{item}</li>
      ))}
    </ul>
  );
}

export default function OperationalHighlights() {
  const { data, isLoading } = useDashboard("operational");
  if (isLoading) return <DashboardSkeleton />;
  const p = data?.payload ?? {};

  const hasAny = p.order_book || p.production_status ||
    (p.major_projects ?? []).length || (p.legal_compliance ?? []).length || (p.exceptional_events ?? []).length;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold tracking-tight">Operational Highlights</h1>
      {!hasAny && (
        <div className="panel p-4 text-sm text-mute">
          Upload a Monthly MIS report and run analysis to populate operational highlights.
        </div>
      )}
      <div className="grid md:grid-cols-2 gap-4">
        <Card title="Order Book" icon={ClipboardList}>
          <TextBlock value={p.order_book ?? ""} />
        </Card>
        <Card title="Production Status" icon={Factory}>
          <TextBlock value={p.production_status ?? ""} />
        </Card>
        <Card title="Major Projects" icon={ListChecks}>
          <ListBlock items={p.major_projects ?? []} />
        </Card>
        <Card title="Legal & Compliance" icon={Gavel}>
          <ListBlock items={p.legal_compliance ?? []} />
        </Card>
        <Card title="Exceptional Events" icon={AlertTriangle}>
          <ListBlock items={p.exceptional_events ?? []} />
        </Card>
      </div>
    </div>
  );
}
