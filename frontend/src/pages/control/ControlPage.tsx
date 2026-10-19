import { FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { farmApi, getApiError, irrigationApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { bandClass, titleCase } from "@/lib/utils";

export default function ControlPage() {
  const client = useQueryClient();
  const zones = useQuery({ queryKey: ["zones"], queryFn: () => farmApi.zones() });
  const active = useQuery({ queryKey: ["active-runs"], queryFn: irrigationApi.active, refetchInterval: 8000 });
  const runs = useQuery({ queryKey: ["runs"], queryFn: () => irrigationApi.runs() });
  const invalidate = () => {
    client.invalidateQueries({ queryKey: ["active-runs"] });
    client.invalidateQueries({ queryKey: ["runs"] });
  };
  const start = useMutation({ mutationFn: irrigationApi.manual, onSuccess: invalidate });
  const pause = useMutation({ mutationFn: irrigationApi.pause, onSuccess: invalidate });
  const resume = useMutation({ mutationFn: irrigationApi.resume, onSuccess: invalidate });
  const stop = useMutation({ mutationFn: irrigationApi.stop, onSuccess: invalidate });

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    start.mutate({ zone: data.get("zone"), minutes: Number(data.get("minutes") || 15), notes: data.get("notes") });
  }

  return (
    <Page title="Irrigation control" lede="Manual watering, pause and resume, and every run currently on the system.">
      <div className="grid-2">
        <form className="card form" onSubmit={onSubmit}>
          <h3>Manual watering</h3>
          {start.isError && <div className="error">{getApiError(start.error)}</div>}
          <label>Zone
            <select className="field" name="zone">{(zones.data?.results ?? []).map((zone) => <option key={zone.id} value={zone.id}>{zone.name}</option>)}</select>
          </label>
          <label>Minutes<input className="field" name="minutes" type="number" defaultValue={15} /></label>
          <label>Notes<input className="field" name="notes" placeholder="Hand water after transplant" /></label>
          <button className="btn-terra" type="submit">Start watering</button>
        </form>
        <section className="card">
          <h3>Live runs</h3>
          {(active.data ?? []).map((run) => (
            <article key={run.id} style={{ marginBottom: 14 }}>
              <div className="factor">
                <strong>{run.zone_name}</strong>
                <span className={bandClass(run.status)}>{run.status}</span>
              </div>
              <p className="muted">{titleCase(run.source)} · {run.planned_minutes} min planned</p>
              <div className="btn-row" style={{ marginTop: 8 }}>
                {run.status === "running" && <button className="btn-ghost" onClick={() => resume.mutate(run.id)}>Pause</button>}
                {run.status === "paused" && <button className="btn-ghost" onClick={() => pause.mutate(run.id)}>Resume</button>}
                <button className="btn-danger" onClick={() => stop.mutate(run.id)}>Stop</button>
              </div>
            </article>
          ))}
          {!active.data?.length && <p className="empty">No irrigation is running.</p>}
        </section>
      </div>
      <section className="card" style={{ marginTop: 14 }}>
        <h3>History</h3>
        <table>
          <thead><tr><th>Zone</th><th>Source</th><th>Status</th><th>Volume</th></tr></thead>
          <tbody>
            {(runs.data?.results ?? []).map((run) => (
              <tr key={run.id}>
                <td>{run.zone_name}</td>
                <td>{titleCase(run.source)}</td>
                <td><span className={bandClass(run.status)}>{run.status}</span></td>
                <td>{run.volume_m3 || "—"} m³</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </Page>
  );
}
