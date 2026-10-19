import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { farmApi, getApiError } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { titleCase } from "@/lib/utils";

export default function FarmDetailPage() {
  const { id } = useParams();
  const client = useQueryClient();
  const farm = useQuery({ queryKey: ["farm", id], queryFn: () => farmApi.farm(id!), enabled: Boolean(id) });
  const fields = useQuery({ queryKey: ["fields", id], queryFn: () => farmApi.fields({ farm: id }), enabled: Boolean(id) });
  const zones = useQuery({ queryKey: ["zones", id], queryFn: () => farmApi.zones({ farm: id }), enabled: Boolean(id) });
  const [open, setOpen] = useState(false);
  const create = useMutation({
    mutationFn: farmApi.createField,
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["fields", id] });
      setOpen(false);
    },
  });

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    create.mutate({
      farm: id,
      name: data.get("name"),
      crop_type: data.get("crop_type"),
      soil_type: data.get("soil_type"),
      irrigation_method: data.get("irrigation_method"),
      planting_date: data.get("planting_date") || null,
      area_hectares: Number(data.get("area_hectares") || 0),
    });
  }

  return (
    <Page title={farm.data?.name || "Farm"} lede={farm.data?.description || farm.data?.address} action={<button className="btn-primary" onClick={() => setOpen(true)}>Add field</button>}>
      {farm.isError && <div className="error">{getApiError(farm.error)}</div>}
      <div className="grid-2">
        <section className="card">
          <h3>Fields</h3>
          <table>
            <thead><tr><th>Field</th><th>Crop</th><th>Soil</th><th>Method</th></tr></thead>
            <tbody>
              {(fields.data?.results ?? []).map((field) => (
                <tr key={field.id}>
                  <td>{field.name}</td>
                  <td>{titleCase(field.crop_type)}</td>
                  <td>{titleCase(field.soil_type)}</td>
                  <td>{titleCase(field.irrigation_method)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
        <section className="card">
          <h3>Zones</h3>
          {(zones.data?.results ?? []).map((zone) => (
            <Link key={zone.id} to={`/zones/${zone.id}`} className="factor">
              <span>{zone.name}</span>
              <span className="muted">{zone.target_moisture_min}–{zone.target_moisture_max}%</span>
            </Link>
          ))}
        </section>
      </div>
      {open && (
        <div className="modal-back" onClick={() => setOpen(false)}>
          <form className="card modal form" onClick={(e) => e.stopPropagation()} onSubmit={onSubmit}>
            <h3>New field</h3>
            <label>Name<input className="field" name="name" required /></label>
            <label>Crop
              <select className="field" name="crop_type">
                {["tomato", "lettuce", "citrus", "grape", "corn", "turf"].map((item) => <option key={item} value={item}>{titleCase(item)}</option>)}
              </select>
            </label>
            <label>Soil
              <select className="field" name="soil_type">
                {["loam", "sandy_loam", "clay", "silt"].map((item) => <option key={item} value={item}>{titleCase(item)}</option>)}
              </select>
            </label>
            <label>Irrigation
              <select className="field" name="irrigation_method">
                {["drip", "sprinkler", "micro_spray", "pivot"].map((item) => <option key={item} value={item}>{titleCase(item)}</option>)}
              </select>
            </label>
            <label>Planting date<input className="field" name="planting_date" type="date" /></label>
            <label>Area<input className="field" name="area_hectares" type="number" step="0.1" /></label>
            <div className="btn-row"><button className="btn-primary">Save field</button></div>
          </form>
        </div>
      )}
    </Page>
  );
}
