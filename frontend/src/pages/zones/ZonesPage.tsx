import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { farmApi, getApiError } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { titleCase } from "@/lib/utils";

export default function ZonesPage() {
  const client = useQueryClient();
  const farms = useQuery({ queryKey: ["farms"], queryFn: farmApi.farms });
  const fields = useQuery({ queryKey: ["fields"], queryFn: () => farmApi.fields() });
  const zones = useQuery({ queryKey: ["zones"], queryFn: () => farmApi.zones() });
  const [open, setOpen] = useState(false);
  const create = useMutation({
    mutationFn: farmApi.createZone,
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["zones"] });
      setOpen(false);
    },
  });

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const name = String(data.get("name"));
    create.mutate({
      farm: data.get("farm"),
      field: data.get("field"),
      name,
      code: name.toLowerCase().replace(/\s+/g, "-").slice(0, 40),
      irrigation_method: data.get("irrigation_method"),
      water_source: data.get("water_source"),
      target_moisture_min: Number(data.get("target_moisture_max")),
      target_moisture_max: Number(data.get("target_moisture_min")),
      flow_limit_lpm: Number(data.get("flow_limit_lpm")),
    });
  }

  return (
    <Page title="Irrigation zones" lede="Moisture targets, flow limits, and approval settings for every watered block." action={<button className="btn-primary" onClick={() => setOpen(true)}>Add zone</button>}>
      {zones.isError && <div className="error">{getApiError(zones.error)}</div>}
      <table className="card">
        <thead><tr><th>Zone</th><th>Farm</th><th>Crop</th><th>Method</th><th>Moisture</th><th>Flow</th></tr></thead>
        <tbody>
          {(zones.data?.results ?? []).map((zone) => (
            <tr key={zone.id}>
              <td><Link to={`/zones/${zone.id}`}><strong>{zone.name}</strong></Link></td>
              <td>{zone.farm_name}</td>
              <td>{titleCase(zone.crop_type)}</td>
              <td>{titleCase(zone.irrigation_method)}</td>
              <td>{zone.target_moisture_min}–{zone.target_moisture_max}%</td>
              <td>{zone.flow_limit_lpm} L/min</td>
            </tr>
          ))}
        </tbody>
      </table>
      {open && (
        <div className="modal-back" onClick={() => setOpen(false)}>
          <form className="card modal form" onClick={(e) => e.stopPropagation()} onSubmit={onSubmit}>
            <h3>New zone</h3>
            <label>Farm
              <select className="field" name="farm">{(farms.data?.results ?? []).map((farm) => <option key={farm.id} value={farm.id}>{farm.name}</option>)}</select>
            </label>
            <label>Field
              <select className="field" name="field">{(fields.data?.results ?? []).map((field) => <option key={field.id} value={field.id}>{field.name}</option>)}</select>
            </label>
            <label>Name<input className="field" name="name" required /></label>
            <label>Method
              <select className="field" name="irrigation_method">
                <option value="drip">Drip</option>
                <option value="sprinkler">Sprinkler</option>
                <option value="micro_spray">Micro spray</option>
              </select>
            </label>
            <label>Water source
              <select className="field" name="water_source">
                <option value="reservoir">Reservoir</option>
                <option value="well">Well</option>
              </select>
            </label>
            <label>Min moisture<input className="field" name="target_moisture_min" type="number" defaultValue={22} /></label>
            <label>Max moisture<input className="field" name="target_moisture_max" type="number" defaultValue={36} /></label>
            <label>Flow limit<input className="field" name="flow_limit_lpm" type="number" defaultValue={30} /></label>
            <button className="btn-primary">Save zone</button>
          </form>
        </div>
      )}
    </Page>
  );
}
