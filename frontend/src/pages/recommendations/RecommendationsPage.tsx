import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getApiError, recApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { bandClass, num } from "@/lib/utils";

export default function RecommendationsPage() {
  const client = useQueryClient();
  const query = useQuery({ queryKey: ["recommendations"], queryFn: () => recApi.list() });
  const generate = useMutation({ mutationFn: recApi.generate, onSuccess: () => client.invalidateQueries({ queryKey: ["recommendations"] }) });
  const approve = useMutation({ mutationFn: recApi.approve, onSuccess: () => client.invalidateQueries({ queryKey: ["recommendations"] }) });
  const reject = useMutation({ mutationFn: recApi.reject, onSuccess: () => client.invalidateQueries({ queryKey: ["recommendations"] }) });

  return (
    <Page title="Smart recommendations" lede="Moisture, crop demand, rainfall, and weather produce watering advice. Approval is required before equipment starts." action={<button className="btn-primary" onClick={() => generate.mutate()}>Generate now</button>}>
      {query.isError && <div className="error">{getApiError(query.error)}</div>}
      <div className="grid-2">
        {(query.data?.results ?? []).map((rec) => (
          <article key={rec.id} className="card">
            <div className="toolbar" style={{ justifyContent: "space-between" }}>
              <h3>{rec.title}</h3>
              <span className={bandClass(rec.status)}>{rec.status}</span>
            </div>
            <p className="muted">{rec.zone_name} · {rec.farm_name}</p>
            <p style={{ margin: "10px 0" }}>{rec.rationale}</p>
            <div className="factor"><span>Suggested</span><b>{rec.suggested_minutes} min · {num(rec.suggested_volume_m3)} m³</b></div>
            <div className="factor"><span>Confidence</span><b>{num(rec.confidence)}%</b></div>
            {rec.factors.map((factor) => (
              <div key={factor.key} className="factor"><span>{factor.label}</span><span className="muted">{factor.detail}</span></div>
            ))}
            {rec.status === "pending" && (
              <div className="btn-row" style={{ marginTop: 12 }}>
                <button className="btn-primary" onClick={() => reject.mutate(rec.id)}>Approve and start</button>
                <button className="btn-ghost" onClick={() => approve.mutate(rec.id)}>Reject</button>
              </div>
            )}
          </article>
        ))}
      </div>
      {!query.data?.results.length && <p className="empty">No recommendations yet. Generate a pass from live moisture and weather.</p>}
    </Page>
  );
}
