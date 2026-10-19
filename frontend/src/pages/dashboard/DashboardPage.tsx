import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { analyticsApi, getApiError } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { num, titleCase } from "@/lib/utils";

export default function DashboardPage() {
  const query = useQuery({ queryKey: ["dashboard"], queryFn: analyticsApi.dashboard, refetchInterval: 15000 });
  const data = query.data;

  return (
    <Page title="Field board" lede="Live moisture, flow, weather, and the irrigation that is running right now.">
      {query.isError && <div className="error">{getApiError(query.error)}</div>}
      <div className="kpis">
        <article className="card stat"><span>Soil moisture</span><b>{num(data?.soil_moisture)}%</b></article>
        <article className="card stat"><span>Water flow</span><b>{num(data?.flow_lpm)} L/m</b></article>
        <article className="card stat"><span>Reservoir</span><b>{num(data?.reservoir_percent)}%</b></article>
        <article className="card stat"><span>Active irrigation</span><b>{data?.active_runs ?? "—"}</b></article>
      </div>
      <div className="kpis">
        <article className="card stat"><span>Temperature</span><b>{num(data?.temperature_c)}°</b></article>
        <article className="card stat"><span>Humidity</span><b>{num(data?.humidity)}%</b></article>
        <article className="card stat"><span>Rain 24h</span><b>{num(data?.rainfall_mm)} mm</b></article>
        <article className="card stat"><span>Devices online</span><b>{data ? `${data.online_devices}/${data.devices}` : "—"}</b></article>
      </div>
      <div className="grid-2">
        <section className="card">
          <h3>Water use</h3>
          <div style={{ height: 240 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.usage_trend ?? []}>
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Area dataKey="volume" stroke="#1f7a63" fill="#b7e4d4" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>
        <section className="card">
          <div className="toolbar" style={{ justifyContent: "space-between" }}>
            <h3>Zone moisture</h3>
            <Link to="/map" className="btn-ghost">Open map</Link>
          </div>
          {(data?.zone_moisture ?? []).map((zone) => (
            <div key={zone.id}>
              <div className="factor">
                <Link to={`/zones/${zone.id}`}><strong>{zone.name}</strong></Link>
                <span>{zone.moisture == null ? "—" : `${zone.moisture.toFixed(1)}%`}</span>
              </div>
              <div className="bar">
                <span style={{ width: `${Math.min(100, zone.moisture ?? 0)}%` }} />
              </div>
              <p className="muted" style={{ fontSize: 12, margin: "4px 0 10px" }}>Target {zone.target_min}–{zone.target_max}%</p>
            </div>
          ))}
        </section>
      </div>
      <div className="grid-3" style={{ marginTop: 14 }}>
        <section className="card">
          <h3>Weather</h3>
          <div className="factor"><span>Condition</span><b>{titleCase(data.weather.condition)}</b></div>
          <div className="factor"><span>Air temp</span><b>{num(data.weather.temperature_c)}°</b></div>
          <div className="factor"><span>ET0</span><b>{num(data?.weather.et0_mm)} mm</b></div>
        </section>
        <section className="card">
          <h3>Device mix</h3>
          {(data?.device_mix ?? []).map((row) => (
            <div key={row.kind} className="factor"><span>{titleCase(row.kind)}</span><b>{row.count}</b></div>
          ))}
        </section>
        <section className="card">
          <h3>Connectivity</h3>
          {(data?.connectivity ?? []).map((row) => (
            <div key={row.connectivity} className="factor"><span>{titleCase(row.connectivity)}</span><b>{row.count}</b></div>
          ))}
          <p className="muted" style={{ marginTop: 12 }}>{data?.open_alerts ?? 0} open alerts · {num(data?.volume_24h)} m³ today</p>
        </section>
      </div>
    </Page>
  );
}
