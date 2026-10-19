import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { farmApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { titleCase } from "@/lib/utils";

export default function MapPage() {
  const farms = useQuery({ queryKey: ["farms"], queryFn: farmApi.farms });
  const farmId = farms.data?.results[0]?.id;
  const map = useQuery({ queryKey: ["farm-map", farmId], queryFn: () => farmApi.map(farmId!), enabled: Boolean(farmId) });
  const [selected, setSelected] = useState<string | null>(null);
  const zone = map.data?.zones.find((item) => item.id === selected) ?? map.data?.zones[0];

  const polygons = useMemo(() => map.data?.zones ?? [], [map.data]);

  return (
    <Page title="Farm map" lede="Field boundaries, irrigation zones, and device positions for the selected farm.">
      <div className="grid-2">
        <section className="card farm-map">
          <svg viewBox="0 0 100 100" preserveAspectRatio="none">
            {polygons.map((item) => {
              const points = (item.boundary?.length ? item.boundary : [[20, 20], [40, 20], [40, 40], [20, 40]])
                .map((pair) => pair.join(" "))
                .join(",");
              const moistureClass = item.name.toLowerCase().includes("tomato 1") ? "dry" : item.name.toLowerCase().includes("lettuce") ? "wet" : "";
              return (
                <polygon
                  key={item.id}
                  points={points}
                  className={`zone-poly ${moistureClass} ${zone?.id === item.id ? "active" : ""}`}
                  onClick={() => setSelected(item.id)}
                />
              );
            })}
            {(map.data?.devices ?? []).map((device) => {
              const x = Number(device.metadata?.map_x ?? 50);
              const y = Number(device.metadata?.map_y ?? 50);
              return <circle key={device.id} cx={x} cy={y} r="1.6" fill={device.connectivity === "online" ? "#0d221c" : "#c46a32"} />;
            })}
          </svg>
        </section>
        <section className="card">
          <h3>{zone?.name || "Select a zone"}</h3>
          {zone ? (
            <>
              <p className="muted">{zone.farm_name} · {titleCase(zone.crop_type)} · {titleCase(zone.irrigation_method)}</p>
              <div className="factor"><span>Moisture window</span><b>{zone.target_moisture_min}–{zone.target_moisture_max}%</b></div>
              <div className="factor"><span>Flow limit</span><b>{zone.flow_limit_lpm} L/min</b></div>
              <div className="factor"><span>Water source</span><b>{titleCase(zone.water_source)}</b></div>
              <div className="btn-row" style={{ marginTop: 16 }}>
                <Link className="btn-primary" to={`/zones/${zone.id}`}>Open zone</Link>
                <Link className="btn-ghost" to="/control">Control</Link>
              </div>
            </>
          ) : (
            <p className="empty">No farm geometry yet.</p>
          )}
          <h3 style={{ marginTop: 22 }}>Fields</h3>
          {(map.data?.fields ?? []).map((field) => (
            <div key={field.id} className="factor">
              <span>{field.name}</span>
              <span className="muted">{titleCase(field.crop_type)}</span>
            </div>
          ))}
        </section>
      </div>
    </Page>
  );
}
