export default function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-panelEdge/50 ${className}`} />;
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-24" />)}
      </div>
      <Skeleton className="h-72" />
    </div>
  );
}
