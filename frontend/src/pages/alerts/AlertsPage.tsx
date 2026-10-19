import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { alertApi, getApiError } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { bandClass, titleCase } from "@/lib/utils";

export default function AlertsPage() {
  const client = useQueryClient();
  const alerts = useQuery({ queryKey: ["alerts"], queryFn: () => alertApi.list() });
  const rules = useQuery({ queryKey: ["alert-rules"], queryFn: alertApi.rules });
  const [open, setOpen] = useState(false);
  const evaluate = useMutation({ mutationFn: alertApi.evaluate, onSuccess: () => client.invalidateQueries({ queryKey: ["alerts"] }) });
  const ack = useMutation({ mutationFn: alertApi.acknowledge, onSuccess: () => client.invalidateQueries({ queryKey: ["alerts"] }) });
  const resolve = useMutation({ mutationFn: alertApi.resolve, onSuccess: () => client.invalidateQueries({ queryKey: ["alerts"] }) });
  const create = useMutation({
    mutationFn: alertApi.createRule,
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["alert-rules"] });
      setOpen(false);
    },
  });

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    create.mutate({
      name: data.get("name"),
      kind: data.get("kind"),
      severity: data.get("severity"),
      threshold: { percent: Number(data.get("percent") || 20) },
    });
  }

  return (
    <Page
      title="Alerts"
      lede="Low moisture, leaks, unusual flow, sensor failures, reservoir levels, pump faults, and disconnected devices."
      action={<div className="btn-row"><button className="btn-ghost" onClick={() => evaluate.mutate()}>Evaluate now</button><button className="btn-primary" onClick={() => setOpen(true)}>New rule</button></div>}
    >
      {alerts.isError && <div className="error">{getApiError(alerts.error)}</div>}
      <div className="grid-2">
        <section className="card">
          <h3>Open events</h3>
          {(alerts.data?.results ?? []).map((alert) => (
            <article key={alert.id} style={{ marginBottom: 14 }}>
              <div className="factor">
                <strong>{alert.title}</strong>
                <span className={bandClass(alert.severity)}>{alert.severity}</span>
              </div>
              <p className="muted">{alert.body}</p>
              <div className="btn-row" style={{ marginTop: 8 }}>
                <button className="btn-ghost" onClick={() => resolve.mutate(alert.id)}>Acknowledge</button>
                <button className="btn-ghost" onClick={() => ack.mutate(alert.id)}>Resolve</button>
              </div>
            </article>
          ))}
        </section>
        <section className="card">
          <h3>Rules</h3>
          {(rules.data?.results ?? []).map((rule) => (
            <div key={rule.id} className="factor">
              <span>{rule.name}</span>
              <span className="muted">{titleCase(rule.kind)}</span>
            </div>
          ))}
        </section>
      </div>
      {open && (
        <div className="modal-back" onClick={() => setOpen(false)}>
          <form className="card modal form" onClick={(e) => e.stopPropagation()} onSubmit={onSubmit}>
            <h3>Alert rule</h3>
            <label>Name<input className="field" name="name" required /></label>
            <label>Kind
              <select className="field" name="kind">
                {["low_soil_moisture", "excessive_watering", "leak", "unusual_flow", "sensor_failure", "low_reservoir", "pump_fault", "disconnected_device"].map((item) => (
                  <option key={item} value={item}>{titleCase(item)}</option>
                ))}
              </select>
            </label>
            <label>Severity
              <select className="field" name="severity">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </label>
            <label>Threshold value<input className="field" name="percent" type="number" defaultValue={20} /></label>
            <button className="btn-primary">Save rule</button>
          </form>
        </div>
      )}
    </Page>
  );
}
