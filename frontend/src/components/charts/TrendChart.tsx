import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Legend, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { formatNum } from "../ui/KpiCard";
import type { SeriesPoint } from "../../types";

const AX = { stroke: "#5A6284", fontSize: 11, fontFamily: "IBM Plex Mono" };

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

const COLORS = ["#7B78FF", "#33D6FF", "#3EE6A8", "#FFB347", "#FF7A93"];

export function MultiLine({ series, kind = "line" }: {
  series: { name: string; data: SeriesPoint[] }[]; kind?: "line" | "bar" | "area";
}) {
  const data = merge(series);
  if (data.length === 0)
    return <div className="h-full grid place-items-center text-mute text-sm">
      No data yet — upload documents and run an analysis.</div>;

  const common = (
    <>
      <CartesianGrid stroke="rgba(146,160,255,.08)" strokeDasharray="3 3" vertical={false} />
      <XAxis dataKey="period" tick={AX} axisLine={false} tickLine={false} />
      <YAxis tick={AX} tickFormatter={(v) => formatNum(v)} width={70} axisLine={false} tickLine={false} />
      <Tooltip contentStyle={{
        background: "rgba(12,15,28,.95)", border: "1px solid rgba(146,160,255,.28)",
        borderRadius: 10, fontFamily: "IBM Plex Mono", fontSize: 12, color: "#E9ECFA",
      }} formatter={(v: number) => formatNum(v)} />
      {series.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
    </>
  );

  return (
    <ResponsiveContainer width="100%" height="100%">
      {kind === "bar" ? (
        <BarChart data={data}>{common}
          {series.map((s, i) => <Bar key={s.name} dataKey={s.name} fill={COLORS[i % COLORS.length]} radius={[4, 4, 0, 0]} animationDuration={900} />)}
        </BarChart>
      ) : kind === "area" ? (
        <AreaChart data={data}>
          <defs>
            {series.map((s, i) => (
              <linearGradient key={s.name} id={`grad-${s.name.replace(/\s+/g, "")}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={COLORS[i % COLORS.length]} stopOpacity={0.35} />
                <stop offset="100%" stopColor={COLORS[i % COLORS.length]} stopOpacity={0} />
              </linearGradient>
            ))}
          </defs>
          {common}
          {series.map((s, i) => <Area key={s.name} dataKey={s.name} stroke={COLORS[i % COLORS.length]}
            fill={`url(#grad-${s.name.replace(/\s+/g, "")})`} strokeWidth={2.2} animationDuration={1000} />)}
        </AreaChart>
      ) : (
        <LineChart data={data}>{common}
          {series.map((s, i) => <Line key={s.name} dataKey={s.name} stroke={COLORS[i % COLORS.length]}
            strokeWidth={2.2} dot={{ r: 3 }} animationDuration={900} />)}
        </LineChart>
      )}
    </ResponsiveContainer>
  );
}
