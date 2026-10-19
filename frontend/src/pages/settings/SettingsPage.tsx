import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { auditApi, farmApi, getApiError, orgApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";

export default function SettingsPage() {
  const client = useQueryClient();
  const settings = useQuery({ queryKey: ["org-settings"], queryFn: orgApi.settings });
  const members = useQuery({ queryKey: ["members"], queryFn: orgApi.members });
  const invitations = useQuery({ queryKey: ["invitations"], queryFn: orgApi.invitations });
  const roles = useQuery({ queryKey: ["roles"], queryFn: orgApi.roles });
  const keys = useQuery({ queryKey: ["api-keys"], queryFn: orgApi.apiKeys });
  const logs = useQuery({ queryKey: ["audit"], queryFn: auditApi.logs });
  const farms = useQuery({ queryKey: ["farms"], queryFn: farmApi.farms });
  const [newKey, setNewKey] = useState("");
  const save = useMutation({ mutationFn: orgApi.saveSettings, onSuccess: () => client.invalidateQueries({ queryKey: ["org-settings"] }) });
  const invite = useMutation({ mutationFn: orgApi.invite, onSuccess: () => client.invalidateQueries({ queryKey: ["invitations"] }) });
  const createKey = useMutation({
    mutationFn: orgApi.createKey,
    onSuccess: (data) => {
      setNewKey(data.key);
      client.invalidateQueries({ queryKey: ["api-keys"] });
    },
  });

  function onSettings(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    save.mutate({
      timezone: data.get("timezone"),
      currency: data.get("currency"),
      water_unit: data.get("water_unit"),
      water_cost_per_unit: data.get("water_cost_per_unit"),
      require_recommendation_approval: data.get("require_recommendation_approval") === "on",
      low_moisture_buffer: Number(data.get("low_moisture_buffer") || 2),
    });
  }

  function onInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    invite.mutate({
      email: data.get("email"),
      role: data.get("role"),
      restrict_to_assigned: data.get("restrict_to_assigned") === "on",
      assigned_farms: data.get("farm") ? [data.get("farm")] : [],
    });
  }

  return (
    <Page title="Organization settings" lede="Roles, invitations, farm-level access, recommendation approval, API keys, and audit history.">
      <div className="grid-2">
        <form className="card form" onSubmit={onSettings}>
          <h3>Operations defaults</h3>
          {save.isError && <div className="error">{getApiError(save.error)}</div>}
          <label>Timezone<input className="field" name="timezone" defaultValue={String(settings.data?.timezone || "UTC")} /></label>
          <label>Currency<input className="field" name="currency" defaultValue={String(settings.data?.currency || "USD")} /></label>
          <label>Water unit<input className="field" name="water_unit" defaultValue={String(settings.data?.water_unit || "m3")} /></label>
          <label>Water cost / unit<input className="field" name="water_cost_per_unit" defaultValue={String(settings.data?.water_cost_per_unit || "0.45")} /></label>
          <label>Low moisture buffer<input className="field" name="low_moisture_buffer" type="number" defaultValue={Number(settings.data?.low_moisture_buffer || 2)} /></label>
          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input type="checkbox" name="require_recommendation_approval" defaultChecked={settings.data?.require_recommendation_approval !== false} />
            Require approval before recommended irrigation starts
          </label>
          <button className="btn-primary">Save settings</button>
        </form>
        <form className="card form" onSubmit={onInvite}>
          <h3>Invite staff</h3>
          <label>Email<input className="field" name="email" type="email" required /></label>
          <label>Role
            <select className="field" name="role">
              <option value="operator">Operator</option>
              <option value="agronomist">Agronomist</option>
              <option value="technician">Technician</option>
              <option value="viewer">Viewer</option>
              <option value="admin">Admin</option>
            </select>
          </label>
          <label>Limit to farm
            <select className="field" name="farm">
              <option value="">All farms</option>
              {(farms.data?.results ?? []).map((farm) => <option key={farm.id} value={farm.id}>{farm.name}</option>)}
            </select>
          </label>
          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input type="checkbox" name="restrict_to_assigned" /> Restrict this person to assigned farms and zones
          </label>
          <button className="btn-primary">Send invitation</button>
          <h3 style={{ marginTop: 18 }}>Pending</h3>
          {(invitations.data?.results ?? []).map((row) => (
            <div key={row.id} className="factor"><span>{row.email}</span><span className="muted">{row.role} · {row.status}</span></div>
          ))}
        </form>
      </div>
      <div className="grid-2" style={{ marginTop: 14 }}>
        <section className="card">
          <h3>Members</h3>
          {(members.data?.results ?? []).map((row) => (
            <div key={row.id} className="factor"><span>{row.user_name || row.user_email}</span><span className="muted">{row.role}</span></div>
          ))}
          <h3 style={{ marginTop: 18 }}>Roles</h3>
          {(roles.data?.results ?? []).map((row) => (
            <div key={row.id} className="factor"><span>{row.name}</span><span className="muted">{row.permissions.length} permissions</span></div>
          ))}
        </section>
        <section className="card">
          <h3>API keys</h3>
          <button className="btn-ghost" onClick={() => createKey.mutate({ name: "Device ingest", scopes: ["devices.write", "devices.read"] })}>Create ingest key</button>
          {newKey && <p className="muted" style={{ marginTop: 8 }}>Copy now: {newKey}</p>}
          {(keys.data?.results ?? []).map((row) => (
            <div key={row.id} className="factor"><span>{row.name} · {row.prefix}</span><button className="btn-danger" onClick={() => orgApi.revokeKey(row.id).then(() => client.invalidateQueries({ queryKey: ["api-keys"] }))}>Revoke</button></div>
          ))}
          <h3 style={{ marginTop: 18 }}>Audit</h3>
          {(logs.data?.results ?? []).slice(0, 8).map((row) => (
            <div key={row.id} className="factor"><span>{row.action} {row.path}</span><span className="muted">{row.actor_email}</span></div>
          ))}
        </section>
      </div>
    </Page>
  );
}
