import { FormEvent, ReactNode, useEffect } from "react";
import { Link, NavLink, Navigate, Outlet, useNavigate } from "react-router-dom";
import { Bell, LogOut } from "lucide-react";
import { authApi } from "@/api/client";
import { useAuthStore } from "@/stores/authStore";

const links = [
  ["Operations", [["/", "Field board"], ["/map", "Farm map"], ["/control", "Irrigation control"]]],
  ["Land", [["/farms", "Farms"], ["/zones", "Zones"], ["/devices", "Devices"]]],
  ["Programs", [["/schedules", "Schedules"], ["/recommendations", "Recommendations"], ["/alerts", "Alerts"]]],
  ["Back office", [["/analytics", "Analytics"], ["/maintenance", "Maintenance"], ["/tasks", "Tasks"], ["/reports", "Reports"], ["/settings", "Settings"]]],
] as const;

export function AppShell() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const memberships = useAuthStore((s) => s.memberships);
  const currentOrgId = useAuthStore((s) => s.currentOrgId);
  const setOrg = useAuthStore((s) => s.setOrg);
  const logout = useAuthStore((s) => s.logout);
  const org = memberships.find((item) => item.organization === currentOrgId);

  function onSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const q = String(data.get("q") || "");
    navigate(`/search?query=${q}`);
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="mark">A</div>
          <div>
            <strong>AquaTerra</strong>
            <span>{org?.organization_name || "Irrigation operations"}</span>
          </div>
        </div>
        {links.map(([label, items]) => (
          <div key={label}>
            <div className="nav-label">{label}</div>
            {items.map(([to, text]) => (
              <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
                {text}
              </NavLink>
            ))}
          </div>
        ))}
      </aside>
      <div className="main">
        <header className="topbar">
          <form onSubmit={onSearch} style={{ flex: 1 }}>
            <input className="search-input" name="q" placeholder="Search farms, zones, devices, alerts" />
          </form>
          {memberships.length > 1 && (
            <select value={currentOrgId ?? ""} onChange={(event) => setOrg(event.target.value)}>
              {memberships.map((item) => (
                <option key={item.organization} value={item.organization}>{item.organization_name}</option>
              ))}
            </select>
          )}
          <Link to="/notifications" className="btn-ghost"><Bell size={16} /></Link>
          <span className="muted">{user?.full_name}</span>
          <button className="btn-ghost" onClick={() => { logout(); navigate("/login"); }}><LogOut size={16} /></button>
        </header>
        <Outlet />
      </div>
    </div>
  );
}

export function ProtectedRoute() {
  const bootstrapped = useAuthStore((s) => s.bootstrapped);
  const token = useAuthStore((s) => s.accessToken);
  const setSession = useAuthStore((s) => s.setSession);
  const setBootstrapped = useAuthStore((s) => s.setBootstrapped);
  const setAccessToken = useAuthStore((s) => s.setAccessToken);

  useEffect(() => {
    let cancelled = false;
    async function hydrate() {
      if (!token) {
        setBootstrapped(true);
        return;
      }
      try {
        const me = await authApi.me();
        if (!cancelled) {
          setSession(token, localStorage.getItem("aquaterra.refresh") || "", me.user, me.memberships);
        }
      } catch {
        if (!cancelled) setAccessToken("");
      } finally {
        if (!cancelled) setBootstrapped(true);
      }
    }
    hydrate();
    return () => {
      cancelled = true;
    };
  }, [token, setAccessToken, setBootstrapped, setSession]);

  if (!bootstrapped) return <div className="page">Loading operations…</div>;
  if (token) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export function Page({ title, lede, action, children }: { title: string; lede?: string; action?: ReactNode; children: ReactNode }) {
  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1>{title}</h1>
          {lede && <p>{lede}</p>}
        </div>
        {action}
      </div>
      {children}
    </div>
  );
}

export function ErrorText({ error }: { error: unknown }) {
  if (!error) return null;
  const message = error instanceof Error ? error.message : "Something went wrong.";
  return <div className="error">{message}</div>;
}
