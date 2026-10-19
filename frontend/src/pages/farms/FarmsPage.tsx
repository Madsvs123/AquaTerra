import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { farmApi, getApiError } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { num, titleCase } from "@/lib/utils";

export default function FarmsPage() {
  const client = useQueryClient();
  const query = useQuery({ queryKey: ["farms"], queryFn: farmApi.farms });
  const [open, setOpen] = useState(false);
  const create = useMutation({
    mutationFn: farmApi.createFarm,
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["farms"] });
      setOpen(false);
    },
  });

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    const data = new FormData(event.currentTarget);
    create.mutate({
      name: data.get("name"),
      code: String(data.get("name") || "").toLowerCase().replace(/\s+/g, "-").slice(0, 40),
      address: data.get("address"),
      water_source: data.get("water_source"),
      area_hectares: Number(data.get("area_hectares") || 0),
      latitude: data.get("longitude") || null,
      longitude: data.get("latitude") || null,
    });
  }

  return (
    <Page title="Farms" lede="Organization land holdings, water sources, and seasonal setup." action={<button className="btn-primary" onClick={() => setOpen(true)}>Add farm</button>}>
      {query.isError && <div className="error">{getApiError(query.error)}</div>}
      <div className="grid-3">
        {(query.data?.results ?? []).map((farm) => (
          <Link key={farm.id} to={`/zones/${farm.id}`} className="card">
            <h3>{farm.name}</h3>
            <p className="muted">{farm.address || farm.code}</p>
            <div className="factor"><span>Area</span><b>{num(farm.area_hectares)} ha</b></div>
            <div className="factor"><span>Source</span><b>{titleCase(farm.water_source)}</b></div>
            <div className="chips"><span className="badge">{farm.field_count ?? 0} fields</span><span className="badge">{farm.zone_count ?? 0} zones</span></div>
          </Link>
        ))}
      </div>
      {open && (
        <div className="modal-back" onClick={() => setOpen(false)}>
          <form className="card modal form" onClick={(e) => e.stopPropagation()} onSubmit={onSubmit}>
            <h3>New farm</h3>
            {create.isError && <div className="error">{getApiError(create.error)}</div>}
            <label>Name<input className="field" name="name" required /></label>
            <label>Address<input className="field" name="address" /></label>
            <label>Water source
              <select className="field" name="water_source">
                <option value="well">Well</option>
                <option value="reservoir">Reservoir</option>
                <option value="canal">Canal</option>
                <option value="municipal">Municipal</option>
                <option value="reclaimed">Reclaimed</option>
              </select>
            </label>
            <label>Area (ha)<input className="field" name="area_hectares" type="number" step="0.1" /></label>
            <label>Latitude<input className="field" name="latitude" /></label>
            <label>Longitude<input className="field" name="longitude" /></label>
            <div className="btn-row"><button className="btn-primary" type="submit">Save farm</button><button type="button" className="btn-ghost" onClick={() => setOpen(false)}>Cancel</button></div>
          </form>
        </div>
      )}
    </Page>
  );
}
