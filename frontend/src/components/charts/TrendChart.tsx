import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Legend, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { formatNum } from "../ui/KpiCard";
import type { SeriesPoint } from "../../types";

const AX = { stroke: "#8CA0C6", fontSize: 11, fontFamily: "IBM Plex Mono" };

export function ChartPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="panel p-4">
      <h3 className="text-xs uppercase tracking-widest text-mute mb-3">{title}</h3>
      <div className="h-64">{children}</div>
    </div>
  );
}

function merge(series: { name: string; data: SeriesPoint[] }[]) {
  const byPeriod: Record<string, Record<string, number | string>> = {};
  for (const s of series)
    for (const p of s.data ?? []) {
      byPeriod[p.period] ??= { period: p.period };
      byPeriod[p.period][s.name] = p.value;
    }
  return Object.values(byPeriod);
}

const COLORS = ["#FFB020", "#2DD4BF", "#60A5FA", "#F87171", "#C084FC"];

export function MultiLine({ series, kind = "line" }: {
  series: { name: string; data: SeriesPoint[] }[]; kind?: "line" | "bar" | "area";
}) {
  const data = merge(series);
  if (data.length === 0)
    return <div className="h-full grid place-items-center text-mute text-sm">
      No data yet — upload documents and run an analysis.</div>;

  const common = (
    <>
      <CartesianGrid stroke="#1E2A44" strokeDasharray="3 3" />
      <XAxis dataKey="period" tick={AX} />
      <YAxis tick={AX} tickFormatter={(v) => formatNum(v)} width={70} />
      <Tooltip contentStyle={{ background: "#111A2E", border: "1px solid #1E2A44", fontFamily: "IBM Plex Mono", fontSize: 12 }}
        formatter={(v: number) => formatNum(v)} />
      {series.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
    </>
  );

  return (
    <ResponsiveContainer width="100%" height="100%">
      {kind === "bar" ? (
        <BarChart data={data}>{common}
          {series.map((s, i) => <Bar key={s.name} dataKey={s.name} fill={COLORS[i % COLORS.length]} radius={[3, 3, 0, 0]} />)}
        </BarChart>
      ) : kind === "area" ? (
        <AreaChart data={data}>{common}
          {series.map((s, i) => <Area key={s.name} dataKey={s.name} stroke={COLORS[i % COLORS.length]}
            fill={COLORS[i % COLORS.length]} fillOpacity={0.15} strokeWidth={2} />)}
        </AreaChart>
      ) : (
        <LineChart data={data}>{common}
          {series.map((s, i) => <Line key={s.name} dataKey={s.name} stroke={COLORS[i % COLORS.length]}
            strokeWidth={2} dot={{ r: 3 }} />)}
        </LineChart>
      )}
    </ResponsiveContainer>
  );
}
