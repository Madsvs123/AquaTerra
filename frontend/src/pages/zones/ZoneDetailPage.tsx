import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { deviceApi, farmApi, irrigationApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { bandClass, titleCase } from "@/lib/utils";

export default function ZoneDetailPage() {
  const { id } = useParams();
  const zone = useQuery({ queryKey: ["zone", id], queryFn: () => farmApi.zone(id!), enabled: Boolean(id) });
  const devices = useQuery({ queryKey: ["devices", id], queryFn: () => deviceApi.list({ zone: id }), enabled: Boolean(id) });
  const runs = useQuery({ queryKey: ["runs", id], queryFn: () => irrigationApi.runs({ zone: id }), enabled: Boolean(id) });
  const data = zone.data;

  return (
    <Page title={data?.name || "Zone"} lede={data ? `${data.farm_name} · ${titleCase(data.crop_type)} on ${titleCase(data.soil_type)}` : "Irrigation zone"}>
      <div className="kpis">
        <article className="card stat"><span>Moisture window</span><b>{data ? `${data.target_moisture_min}–${data.target_moisture_max}%` : "—"}</b></article>
        <article className="card stat"><span>Flow limit</span><b>{data?.flow_limit_lpm ?? "—"}</b></article>
        <article className="card stat"><span>Season</span><b>{titleCase(data?.season)}</b></article>
        <article className="card stat"><span>Approval</span><b>{data?.require_recommendation_approval ? "Required" : "Optional"}</b></article>
      </div>
      <div className="grid-2">
        <section className="card">
          <h3>Devices</h3>
          {(devices.data?.results ?? []).map((device) => (
            <div key={device.id} className="factor">
              <span>{device.name}</span>
              <span className={bandClass(device.connectivity)}>{device.connectivity}</span>
            </div>
          ))}
        </section>
        <section className="card">
          <h3>Recent irrigation</h3>
          {(runs.data?.results ?? []).map((run) => (
            <div key={run.id} className="factor">
              <span>{titleCase(run.source)} · {run.planned_minutes} min</span>
              <span className={bandClass(run.status)}>{run.status}</span>
            </div>
          ))}
        </section>
      </div>
    </Page>
  );
}
