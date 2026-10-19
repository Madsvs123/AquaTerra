import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { analyticsApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { money, num } from "@/lib/utils";

export default function AnalyticsPage() {
  const query = useQuery({ queryKey: ["water-analytics"], queryFn: () => analyticsApi.water(14) });
  const data = query.data;

  return (
    <Page title="Water analytics" lede="Consumption by farm, field, zone, and crop, with efficiency, cost, and savings against the prior period.">
      <div className="kpis">
        <article className="card stat"><span>Volume</span><b>{money(data?.volume)} m³</b></article>
        <article className="card stat"><span>Cost</span><b>{num(data?.cost)}</b></article>
        <article className="card stat"><span>Efficiency</span><b>{num(data?.efficiency)}%</b></article>
        <article className="card stat"><span>Saved vs prior</span><b>{num(data?.saved_volume)} m³</b></article>
      </div>
      <section className="card">
        <h3>History</h3>
        <div style={{ height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data?.history ?? []}>
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="volume" fill="#1f7a63" radius={8} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
      <div className="grid-3" style={{ marginTop: 14 }}>
        <section className="card">
          <h3>By farm</h3>
          {(data?.by_farm ?? []).map((row) => <div key={row.id} className="factor"><span>{row.name}</span><b>{num(row.volume)}</b></div>)}
        </section>
        <section className="card">
          <h3>By zone</h3>
          {(data?.by_zone ?? []).map((row) => <div key={row.id} className="factor"><span>{row.name}</span><b>{num(row.volume)}</b></div>)}
        </section>
        <section className="card">
          <h3>By crop</h3>
          {(data?.by_crop ?? []).map((row) => <div key={row.name} className="factor"><span>{row.name}</span><b>{num(row.volume)}</b></div>)}
        </section>
      </div>
    </Page>
  );
}
