import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { reportApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";
import { titleCase } from "@/lib/utils";

export default function ReportsPage() {
  const client = useQueryClient();
  const catalog = useQuery({ queryKey: ["report-catalog"], queryFn: reportApi.catalog });
  const runs = useQuery({ queryKey: ["report-runs"], queryFn: reportApi.runs });
  const run = useMutation({ mutationFn: reportApi.run, onSuccess: () => client.invalidateQueries({ queryKey: ["report-runs"] }) });

  return (
    <Page title="Reports" lede="Usage, efficiency, alerts, device health, maintenance, crop consumption, and cost exports.">
      <div className="chips" style={{ marginBottom: 16 }}>
        {(catalog.data?.kinds ?? []).map((kind) => (
          <button key={kind.key} className="btn-ghost" onClick={() => run.mutate(kind.key)}>{kind.label}</button>
        ))}
      </div>
      {(runs.data?.results ?? []).map((item) => (
        <section key={item.id} className="card" style={{ marginBottom: 12 }}>
          <div className="toolbar" style={{ justifyContent: "space-between" }}>
            <h3>{item.result.title || titleCase(item.kind)}</h3>
            <a className="btn-ghost" href={reportApi.exportUrl(item.result.title || item.kind)}>Export CSV</a>
          </div>
          <p className="muted">{item.created_at.replace("T", " ").slice(0, 16)}</p>
        </section>
      ))}
    </Page>
  );
}
