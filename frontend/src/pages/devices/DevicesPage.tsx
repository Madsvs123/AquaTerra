import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { deviceApi, farmApi, getApiError } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { bandClass, titleCase } from "@/lib/utils";

export default function DevicesPage() {
  const client = useQueryClient();
  const devices = useQuery({ queryKey: ["devices"], queryFn: () => deviceApi.list() });
  const farms = useQuery({ queryKey: ["farms"], queryFn: farmApi.farms });
  const zones = useQuery({ queryKey: ["zones"], queryFn: () => farmApi.zones() });
  const [open, setOpen] = useState(false);
  const create = useMutation({
    mutationFn: deviceApi.create,
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["devices"] });
      setOpen(false);
    },
  });

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    create.mutate({
      farm: data.get("farm"),
      zone: data.get("zone") || null,
      name: data.get("name"),
      serial_number: data.get("serial_number"),
      kind: data.get("kind"),
    });
  }

  return (
    <Page title="Devices" lede="Controllers, valves, pumps, meters, and every sensor reporting into AquaTerra." action={<button className="btn-primary" onClick={() => setOpen(true)}>Register device</button>}>
      {devices.isError && <div className="error">{getApiError(devices.error)}</div>}
      <table className="card">
        <thead><tr><th>Device</th><th>Kind</th><th>Zone</th><th>Health</th><th>Link</th><th>Battery</th></tr></thead>
        <tbody>
          {(devices.data?.results ?? []).map((device) => (
            <tr key={device.id}>
              <td><Link to={`/devices/${device.id}`}><strong>{device.name}</strong></Link><div className="muted">{device.serial_number}</div></td>
              <td>{titleCase(device.kind)}</td>
              <td>{device.zone_name || "Farm-wide"}</td>
              <td><span className={bandClass(device.health)}>{device.health}</span></td>
              <td><span className={bandClass(device.connectivity)}>{device.connectivity}</span></td>
              <td>{device.battery_percent == null ? "—" : `${device.battery_percent}%`}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {open && (
        <div className="modal-back" onClick={() => setOpen(false)}>
          <form className="card modal form" onClick={(e) => e.stopPropagation()} onSubmit={onSubmit}>
            <h3>Register device</h3>
            <label>Name<input className="field" name="name" required /></label>
            <label>Serial<input className="field" name="serial_number" required /></label>
            <label>Kind
              <select className="field" name="kind">
                {["soil_moisture", "temperature", "humidity", "flow_meter", "weather_station", "pump", "valve", "controller", "reservoir"].map((item) => (
                  <option key={item} value={item}>{titleCase(item)}</option>
                ))}
              </select>
            </label>
            <label>Farm<select className="field" name="farm">{(farms.data?.results ?? []).map((farm) => <option key={farm.id} value={farm.id}>{farm.name}</option>)}</select></label>
            <label>Zone
              <select className="field" name="zone">
                <option value="">Farm-wide</option>
                {(zones.data?.results ?? []).map((zone) => <option key={zone.id} value={zone.id}>{zone.name}</option>)}
              </select>
            </label>
            <button className="btn-primary">Save device</button>
          </form>
        </div>
      )}
    </Page>
  );
}
