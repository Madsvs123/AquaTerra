import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { farmApi, getApiError, irrigationApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { dayName, titleCase } from "@/lib/utils";

export default function SchedulesPage() {
  const client = useQueryClient();
  const programs = useQuery({ queryKey: ["programs"], queryFn: irrigationApi.programs });
  const farms = useQuery({ queryKey: ["farms"], queryFn: farmApi.farms });
  const zones = useQuery({ queryKey: ["zones"], queryFn: () => farmApi.zones() });
  const [open, setOpen] = useState(false);
  const create = useMutation({
    mutationFn: async (body: Record<string, unknown>) => {
      const program = await irrigationApi.createProgram({
        farm: body.farm,
        name: body.name,
        kind: body.kind,
        seasonal_adjustment_percent: Number(body.seasonal_adjustment_percent || 0),
      });
      await irrigationApi.createSlot({
        program: program.id,
        zone: body.zone,
        day_of_week: Number(body.day_of_week) + 1,
        start_time: body.start_time,
        duration_minutes: Number(body.duration_minutes),
        flow_limit_lpm: Number(body.flow_limit_lpm || 0) || null,
      });
    },
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["programs"] });
      setOpen(false);
    },
  });

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget).entries());
    create.mutate(data);
  }

  return (
    <Page title="Schedules" lede="Daily and weekly programs, zone durations, flow limits, and seasonal adjustments." action={<button className="btn-primary" onClick={() => setOpen(true)}>New program</button>}>
      {(programs.data?.results ?? []).map((program) => (
        <section key={program.id} className="card" style={{ marginBottom: 14 }}>
          <div className="toolbar" style={{ justifyContent: "space-between" }}>
            <div>
              <h3>{program.name}</h3>
              <p className="muted">{program.farm_name} · {titleCase(program.kind)} · {program.seasonal_adjustment_percent}% seasonal</p>
            </div>
            <span className="badge">{program.is_active ? "Active" : "Paused"}</span>
          </div>
          <table>
            <thead><tr><th>Day</th><th>Zone</th><th>Start</th><th>Duration</th><th>Flow</th></tr></thead>
            <tbody>
              {program.slots.map((slot) => (
                <tr key={slot.id}>
                  <td>{dayName(slot.day_of_week)}</td>
                  <td>{slot.zone_name}</td>
                  <td>{slot.start_time}</td>
                  <td>{slot.duration_minutes} min</td>
                  <td>{slot.flow_limit_lpm || "zone default"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}
      {open && (
        <div className="modal-back" onClick={() => setOpen(false)}>
          <form className="card modal form" onClick={(e) => e.stopPropagation()} onSubmit={onSubmit}>
            <h3>Program + first slot</h3>
            {create.isError && <div className="error">{getApiError(create.error)}</div>}
            <label>Name<input className="field" name="name" required /></label>
            <label>Farm<select className="field" name="farm">{(farms.data?.results ?? []).map((farm) => <option key={farm.id} value={farm.id}>{farm.name}</option>)}</select></label>
            <label>Kind
              <select className="field" name="kind">
                <option value="weekly">Weekly</option>
                <option value="daily">Daily</option>
                <option value="recurring">Recurring</option>
                <option value="seasonal">Seasonal</option>
              </select>
            </label>
            <label>Seasonal adjustment %<input className="field" name="seasonal_adjustment_percent" type="number" defaultValue={0} /></label>
            <label>Zone<select className="field" name="zone">{(zones.data?.results ?? []).map((zone) => <option key={zone.id} value={zone.id}>{zone.name}</option>)}</select></label>
            <label>Day
              <select className="field" name="day_of_week">
                {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].map((day, index) => <option key={day} value={index}>{day}</option>)}
              </select>
            </label>
            <label>Start<input className="field" name="start_time" type="time" required /></label>
            <label>Duration<input className="field" name="duration_minutes" type="number" defaultValue={20} /></label>
            <label>Flow limit<input className="field" name="flow_limit_lpm" type="number" /></label>
            <button className="btn-primary">Save program</button>
          </form>
        </div>
      )}
    </Page>
  );
}
