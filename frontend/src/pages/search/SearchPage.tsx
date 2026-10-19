import { useQuery } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { searchApi } from "@/api/client";
import { Page } from "@/components/layout/AppShell";

export default function SearchPage() {
  const [params] = useSearchParams();
  const q = params.get("q") || "";
  const query = useQuery({ queryKey: ["search", q], queryFn: () => searchApi.query(q), enabled: Boolean(q) });
  const groups = [
    ["Farms", "/zones/", query.data?.farms],
    ["Zones", "/devices/", query.data?.zones],
    ["Devices", "/devices/", query.data?.devices],
    ["Alerts", "/alerts", query.data?.alerts],
    ["Programs", "/schedules", query.data?.programs],
    ["Work orders", "/maintenance", query.data?.work_orders],
  ] as const;

  return (
    <Page title="Search" lede={q ? `Results for “${q}”` : "Search the operations workspace."}>
      {groups.map(([label, href, rows]) => (
        <section key={label} className="card" style={{ marginBottom: 12 }}>
          <h3>{label}</h3>
          {(rows ?? []).map((row) => (
            <Link key={row.id} to={href.endsWith("/") ? `${href}${row.id}` : href} className="factor">
              <span>{row.label}</span>
              <span className="muted">{row.meta}</span>
            </Link>
          ))}
          {!rows?.length && <p className="empty">No matches.</p>}
        </section>
      ))}
    </Page>
  );
}
