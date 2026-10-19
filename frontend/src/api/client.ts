import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";
import { REFRESH_KEY, useAuthStore } from "@/stores/authStore";
import type {
  AlertItem,
  Asset,
  AuthResponse,
  DashboardData,
  Device,
  Farm,
  Field,
  IrrigationRun,
  Membership,
  NotificationItem,
  Paginated,
  Program,
  Reading,
  Recommendation,
  ReportRun,
  SearchResults,
  User,
  WaterAnalytics,
  WorkOrder,
  WorkTask,
  Zone,
} from "@/types";

export const api = axios.create({ baseURL: "" });

api.interceptors.request.use((config) => {
  const { accessToken, currentOrgId } = useAuthStore.getState();
  config.headers = config.headers ?? {};
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`;
  if (currentOrgId) config.headers["X-Organization"] = currentOrgId;
  return config;
});

let refreshing: Promise<string> | null = null;

async function refreshAccess() {
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (!refresh) throw new Error("Missing refresh token");
  const { data } = await axios.post<{ access: string; refresh?: string }>("/api/auth/refresh/", { refresh });
  if (data.refresh) localStorage.setItem(REFRESH_KEY, data.refresh);
  useAuthStore.getState().setAccessToken(data.access);
  return data.access;
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    if (error.response?.status === 200 && original && !original._retry && !original.url?.includes("/api/auth/")) {
      original._retry = true;
      try {
        refreshing ??= refreshAccess().finally(() => {
          refreshing = null;
        });
        original.headers.Authorization = `Bearer ${await refreshing}`;
        return api(original);
      } catch {
        useAuthStore.getState().logout();
      }
    }
    return Promise.reject(error);
  },
);

export function getApiError(error: unknown) {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as Record<string, unknown> | string | undefined;
    if (typeof data === "string") return data;
    if (data && typeof data.detail === "string") return data.detail;
    if (data && typeof data === "object") {
      return Object.entries(data)
        .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(" ") : String(value)}`)
        .join(" ");
    }
    return error.message;
  }
  return error instanceof Error ? error.message : "Request failed.";
}

async function page<T>(url: string, params?: Record<string, unknown>): Promise<Paginated<T>> {
  const { data } = await api.get<Paginated<T> | T[]>(url, { params });
  return Array.isArray(data) ? { count: data.length, next: null, previous: null, results: data } : data;
}

export const authApi = {
  login: (body: { email: string; password: string }) => api.post<AuthResponse>("/api/auth/logins/", body).then((r) => r.data),
  register: (body: Record<string, string>) => api.post<AuthResponse>("/api/auth/register/", body).then((r) => r.data),
  me: () => api.get<{ user: User; memberships: Membership[]; permissions: string[] }>("/api/auth/me/").then((r) => r.data),
  accept: (body: Record<string, string>) => api.post<AuthResponse>("/api/auth/invitations/accept/", body).then((r) => r.data),
};

export const orgApi = {
  list: () => page<{ id: string; name: string; slug: string; timezone: string; currency: string; water_unit: string; settings: Record<string, unknown> }>("/api/organizations/orgs/"),
  settings: () => api.get<Record<string, unknown>>("/api/organizations/settings/").then((r) => r.data),
  saveSettings: (body: Record<string, unknown>) => api.patch("/api/organizations/settings/", body).then((r) => r.data),
  teams: () => page<{ id: string; name: string; description: string }>("/api/organizations/teams/"),
  createTeam: (body: Record<string, unknown>) => api.post("/api/organizations/teams/", body).then((r) => r.data),
  members: () => page<Membership & { user_email: string; user_name: string }>("/api/organizations/memberships/"),
  invitations: () => page<{ id: string; email: string; role: string; status: string; expires_at: string }>("/api/auth/invitations/"),
  invite: (body: Record<string, unknown>) => api.post("/api/auth/invitations/", body).then((r) => r.data),
  roles: () => page<{ id: string; name: string; slug: string; base_role: string; permissions: string[] }>("/api/auth/roles/"),
  createRole: (body: Record<string, unknown>) => api.post("/api/auth/roles/", body).then((r) => r.data),
  apiKeys: () => page<{ id: string; name: string; prefix: string; scopes: string[]; revoked_at: string | null }>("/api/auth/api-keys/"),
  createKey: (body: Record<string, unknown>) => api.post<{ id: string; key: string; prefix: string }>("/api/auth/api-keys/", body).then((r) => r.data),
  revokeKey: (id: string) => api.delete(`/api/auth/api-keys/${id}/`),
};

export const farmApi = {
  farms: () => page<Farm>("/api/farms/farms/"),
  farm: (id: string) => api.get<Farm>(`/api/farms/farms/${id}/`).then((r) => r.data),
  createFarm: (body: Record<string, unknown>) => api.post<Farm>("/api/farms/farms/", body).then((r) => r.data),
  map: (id: string) => api.get<{ farm: Farm; fields: Field[]; zones: Zone[]; devices: Device[] }>(`/api/farms/farms/${id}/map/`).then((r) => r.data),
  fields: (params?: Record<string, unknown>) => page<Field>("/api/farms/fields/", params),
  createField: (body: Record<string, unknown>) => api.post<Field>("/api/farms/fields/", body).then((r) => r.data),
  zones: (params?: Record<string, unknown>) => page<Zone>("/api/farms/zones/", params),
  zone: (id: string) => api.get<Zone>(`/api/farms/zones/${id}/`).then((r) => r.data),
  createZone: (body: Record<string, unknown>) => api.post<Zone>("/api/farms/zones/", body).then((r) => r.data),
  sites: () => page<{ id: string; name: string; farm: string; farm_name: string }>("/api/farms/sites/"),
  createSite: (body: Record<string, unknown>) => api.post("/api/farms/sites/", body).then((r) => r.data),
};

export const deviceApi = {
  list: (params?: Record<string, unknown>) => page<Device>("/api/devices/inventory/", params),
  get: (id: string) => api.get<Device>(`/api/devices/inventory/${id}/`).then((r) => r.data),
  create: (body: Record<string, unknown>) => api.post<Device>("/api/devices/inventory/", body).then((r) => r.data),
  readings: (id: string) => api.get<Reading[]>(`/api/devices/inventory/${id}/readings/`).then((r) => r.data),
  allReadings: (params?: Record<string, unknown>) => page<Reading>("/api/devices/readings/", params),
};

export const irrigationApi = {
  programs: () => page<Program>("/api/irrigation/programs/"),
  createProgram: (body: Record<string, unknown>) => api.post<Program>("/api/irrigation/programs/", body).then((r) => r.data),
  createSlot: (body: Record<string, unknown>) => api.post("/api/irrigation/slots/", body).then((r) => r.data),
  runs: (params?: Record<string, unknown>) => page<IrrigationRun>("/api/irrigation/runs/", params),
  active: () => api.get<IrrigationRun[]>("/api/irrigation/active/").then((r) => r.data),
  manual: (body: Record<string, unknown>) => api.post<IrrigationRun>("/api/irrigation/manual/", body).then((r) => r.data),
  pause: (id: string) => api.post<IrrigationRun>(`/api/irrigation/runs/${id}/pause/`).then((r) => r.data),
  resume: (id: string) => api.post<IrrigationRun>(`/api/irrigation/runs/${id}/resume/`).then((r) => r.data),
  stop: (id: string) => api.post<IrrigationRun>(`/api/irrigation/runs/${id}/stop/`).then((r) => r.data),
};

export const recApi = {
  list: (params?: Record<string, unknown>) => page<Recommendation>("/api/recommendations/items/", params),
  generate: () => api.post<{ count: number; created: Recommendation[] }>("/api/recommendations/generate/").then((r) => r.data),
  approve: (id: string) => api.post(`/api/recommendations/items/${id}/approve/`).then((r) => r.data),
  reject: (id: string) => api.post(`/api/recommendations/items/${id}/reject/`).then((r) => r.data),
};

export const alertApi = {
  list: (params?: Record<string, unknown>) => page<AlertItem>("/api/alerts/events/", params),
  rules: () => page<{ id: string; name: string; kind: string; severity: string; is_active: boolean; threshold: Record<string, unknown> }>("/api/alerts/rules/"),
  createRule: (body: Record<string, unknown>) => api.post("/api/alerts/rules/", body).then((r) => r.data),
  acknowledge: (id: string) => api.post(`/api/alerts/events/${id}/acknowledge/`).then((r) => r.data),
  resolve: (id: string) => api.post(`/api/alerts/events/${id}/resolve/`).then((r) => r.data),
  evaluate: () => api.post("/api/alerts/evaluate/").then((r) => r.data),
};

export const analyticsApi = {
  dashboard: () => api.get<DashboardData>("/api/analytics/dashboards/").then((r) => r.data),
  water: (days = 14) => api.get<WaterAnalytics>("/api/analytics/water/", { params: { days } }).then((r) => r.data),
};

export const maintenanceApi = {
  assets: () => page<Asset>("/api/maintenance/assets/"),
  createAsset: (body: Record<string, unknown>) => api.post<Asset>("/api/maintenance/assets/", body).then((r) => r.data),
  workOrders: () => page<WorkOrder>("/api/maintenance/work-orders/"),
  createWorkOrder: (body: Record<string, unknown>) => api.post<WorkOrder>("/api/maintenance/work-orders/", body).then((r) => r.data),
  inspections: () => page<{ id: string; asset_name: string; inspected_on: string; result: string; notes: string }>("/api/maintenance/inspections/"),
  createInspection: (body: Record<string, unknown>) => api.post("/api/maintenance/inspections/", body).then((r) => r.data),
  schedules: () => page<{ id: string; asset_name: string; title: string; next_due_on: string; interval_days: number }>("/api/maintenance/schedules/"),
};

export const workApi = {
  list: () => page<WorkTask>("/api/work/tasks/"),
  create: (body: Record<string, unknown>) => api.post<WorkTask>("/api/work/tasks/", body).then((r) => r.data),
  update: (id: string, body: Record<string, unknown>) => api.patch(`/api/work/tasks/${id}/`, body).then((r) => r.data),
};

export const reportApi = {
  catalog: () => api.get<{ kinds: { key: string; label: string }[] }>("/api/reports/catalog/").then((r) => r.data),
  run: (kind: string) => api.post<ReportRun>("/api/reports/run/", { kind }).then((r) => r.data),
  runs: () => page<ReportRun>("/api/reports/runs/"),
  exportUrl: (kind: string) => `/api/reports/export/?kind=${encodeURIComponent(kind)}`,
};

export const notifyApi = {
  list: () => page<NotificationItem>("/api/notifications/inbox/"),
  read: (id: string) => api.post(`/api/notifications/inbox/${id}/read/`).then((r) => r.data),
  readAll: () => api.post("/api/notifications/inbox/read_all/").then((r) => r.data),
};

export const auditApi = {
  logs: () => page<{ id: string; actor_email: string | null; action: string; path: string; status_code: number; created_at: string }>("/api/audit/logs/"),
};

export const searchApi = {
  query: (q: string) => api.get<SearchResults>("/api/search/", { params: { q } }).then((r) => r.data),
};

export const weatherApi = {
  list: () => page<{ id: string; farm_name: string; observed_at: string; temperature_c: number; humidity: number; precipitation_mm: number; et0_mm: number; condition: string }>("/api/weather/observations/"),
  refresh: (farm?: string) => api.post("/api/weather/refresh/", farm ? { farm } : {}).then((r) => r.data),
};
