import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { deviceApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { bandClass, num, titleCase } from "@/lib/utils";

export default function DeviceDetailPage() {
  const { id } = useParams();
  const device = useQuery({ queryKey: ["device", id], queryFn: () => deviceApi.get(id!), enabled: Boolean(id) });
  const readings = useQuery({ queryKey: ["readings", id], queryFn: () => deviceApi.readings(id!), enabled: Boolean(id) });
  const data = device.data;
  const chart = (readings.data ?? []).map((row) => ({
    time: row.recorded_at.slice(11, 16),
    moisture: row.soil_moisture,
    flow: row.flow_lpm,
    temp: row.temperature_c,
  }));

  return (
    <Page title={data?.name || "Device"} lede={data ? `${titleCase(data.kind)} · ${data.serial_number}` : "IoT device"}>
      <div className="kpis">
        <article className="card stat"><span>Health</span><b className={bandClass(data?.health)}>{titleCase(data?.health)}</b></article>
        <article className="card stat"><span>Connectivity</span><b>{titleCase(data?.connectivity)}</b></article>
        <article className="card stat"><span>Battery</span><b>{data?.battery_percent ?? "—"}%</b></article>
        <article className="card stat"><span>Last seen</span><b>{data?.last_seen_at ? data.last_seen_at.slice(11, 16) : "—"}</b></article>
      </div>
      <section className="card">
        <h3>Historical readings</h3>
        <div style={{ height: 280 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chart}>
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="moisture" stroke="#1f7a63" dot={false} />
              <Line type="monotone" dataKey="flow" stroke="#c46a32" dot={false} />
              <Line type="monotone" dataKey="temp" stroke="#2f8f9a" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <table>
          <thead><tr><th>Time</th><th>Moisture</th><th>Temp</th><th>Humidity</th><th>Flow</th></tr></thead>
          <tbody>
            {(readings.data ?? []).slice(0, 12).map((row) => (
              <tr key={row.id}>
                <td>{row.recorded_at.replace("T", " ").slice(0, 16)}</td>
                <td>{num(row.soil_moisture)}</td>
                <td>{num(row.temperature_c)}</td>
                <td>{num(row.humidity)}</td>
                <td>{num(row.flow_lpm)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </Page>
  );
}
