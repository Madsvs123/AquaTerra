import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { farmApi, maintenanceApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { bandClass, titleCase } from "@/lib/utils";

export default function MaintenancePage() {
  const client = useQueryClient();
  const assets = useQuery({ queryKey: ["assets"], queryFn: maintenanceApi.assets });
  const orders = useQuery({ queryKey: ["work-orders"], queryFn: maintenanceApi.workOrders });
  const inspections = useQuery({ queryKey: ["inspections"], queryFn: maintenanceApi.inspections });
  const farms = useQuery({ queryKey: ["farms"], queryFn: farmApi.farms });
  const [tab, setTab] = useState<"assets" | "orders" | "inspections">("orders");
  const [open, setOpen] = useState(false);
  const createAsset = useMutation({ mutationFn: maintenanceApi.createAsset, onSuccess: () => client.invalidateQueries({ queryKey: ["assets"] }) });
  const createOrder = useMutation({
    mutationFn: maintenanceApi.createWorkOrder,
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["work-orders"] });
      setOpen(false);
    },
  });

  function onAsset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    createAsset.mutate({ farm: data.get("farm"), name: data.get("name"), kind: data.get("kind"), serial_number: data.get("serial_number") });
  }

  function onOrder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    createOrder.mutate({
      farm: data.get("farm"),
      asset: data.get("asset"),
      title: data.get("title"),
      details: data.get("details"),
      due_on: data.get("due_on") || null,
    });
  }

  return (
    <Page title="Maintenance" lede="Pumps, valves, controllers, filters, sensors, inspections, and technician work." action={<button className="btn-primary" onClick={() => setOpen(true)}>New work order</button>}>
      <div className="tabs">
        {(["orders", "assets", "inspections"] as const).map((item) => (
          <button key={item} className={`tab${tab === item ? " active" : ""}`} onClick={() => setTab(item)}>{titleCase(item)}</button>
        ))}
      </div>
      {tab === "orders" && (
        <table className="card">
          <thead><tr><th>Work</th><th>Asset</th><th>Farm</th><th>Status</th><th>Due</th></tr></thead>
          <tbody>
            {(orders.data?.results ?? []).map((row) => (
              <tr key={row.id}>
                <td>{row.title}</td>
                <td>{row.asset_name}</td>
                <td>{row.farm_name}</td>
                <td><span className={bandClass(row.status)}>{row.status}</span></td>
                <td>{row.due_on || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {tab === "assets" && (
        <div className="grid-2">
          <section className="card">
            {(assets.data?.results ?? []).map((asset) => (
              <div key={asset.id} className="factor"><span>{asset.name}</span><span className="muted">{titleCase(asset.kind)}</span></div>
            ))}
          </section>
          <form className="card form" onSubmit={onAsset}>
            <h3>Register asset</h3>
            <label>Name<input className="field" name="name" required /></label>
            <label>Kind
              <select className="field" name="kind">
                {["pump", "valve", "controller", "filter", "sensor"].map((item) => <option key={item} value={item}>{titleCase(item)}</option>)}
              </select>
            </label>
            <label>Serial<input className="field" name="serial_number" /></label>
            <label>Farm<select className="field" name="farm">{(farms.data?.results ?? []).map((farm) => <option key={farm.id} value={farm.id}>{farm.name}</option>)}</select></label>
            <button className="btn-primary">Save asset</button>
          </form>
        </div>
      )}
      {tab === "inspections" && (
        <section className="card">
          {(inspections.data?.results ?? []).map((row) => (
            <div key={row.id} className="factor"><span>{row.asset_name} · {row.inspected_on}</span><span className={bandClass(row.result)}>{row.result}</span></div>
          ))}
        </section>
      )}
      {open && (
        <div className="modal-back" onClick={() => setOpen(false)}>
          <form className="card modal form" onClick={(e) => e.stopPropagation()} onSubmit={onOrder}>
            <h3>Work order</h3>
            <label>Title<input className="field" name="title" required /></label>
            <label>Farm<select className="field" name="farm">{(farms.data?.results ?? []).map((farm) => <option key={farm.id} value={farm.id}>{farm.name}</option>)}</select></label>
            <label>Asset<select className="field" name="asset">{(assets.data?.results ?? []).map((asset) => <option key={asset.id} value={asset.id}>{asset.name}</option>)}</select></label>
            <label>Due<input className="field" name="due_on" type="date" /></label>
            <label>Details<textarea className="field" name="details" rows={3} /></label>
            <button className="btn-primary">Create</button>
          </form>
        </div>
      )}
    </Page>
  );
}
