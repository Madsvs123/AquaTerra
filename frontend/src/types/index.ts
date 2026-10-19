export type Paginated<T> = { count: number; next: string | null; previous: string | null; results: T[] };

export type Membership = {
  id: string;
  organization: string;
  organization_name: string;
  organization_slug: string;
  role: string;
  team: string | null;
  team_name: string | null;
  is_default: boolean;
  is_active: boolean;
  restrict_to_assigned: boolean;
};

export type User = { id: string; email: string; full_name: string; title: string; phone?: string; is_active: boolean };
export type AuthResponse = { access: string; refresh: string; user: User; memberships: Membership[] };

export type Farm = {
  id: string;
  name: string;
  code: string;
  description: string;
  address: string;
  latitude: string | number | null;
  longitude: string | number | null;
  area_hectares: string | number | null;
  water_source: string;
  timezone: string;
  seasonal_config: Record<string, unknown>;
  boundary: number[][];
  is_active: boolean;
  site_count?: number;
  field_count?: number;
  zone_count?: number;
};

export type Field = {
  id: string;
  farm: string;
  farm_name: string;
  site: string | null;
  site_name: string | null;
  name: string;
  crop_type: string;
  soil_type: string;
  irrigation_method: string;
  planting_date: string | null;
  area_hectares: string | number | null;
  boundary: number[][];
};

export type Zone = {
  id: string;
  farm: string;
  farm_name: string;
  field: string;
  field_name: string;
  crop_type: string;
  soil_type: string;
  name: string;
  code: string;
  irrigation_method: string;
  water_source: string;
  target_moisture_min: string | number;
  target_moisture_max: string | number;
  flow_limit_lpm: string | number;
  area_hectares: string | number | null;
  season: string;
  boundary: number[][];
  require_recommendation_approval: boolean;
  is_active: boolean;
};

export type Device = {
  id: string;
  farm: string;
  farm_name: string;
  zone: string | null;
  zone_name: string | null;
  name: string;
  serial_number: string;
  kind: string;
  connectivity: string;
  health: string;
  battery_percent: number | null;
  last_seen_at: string | null;
  last_error: string;
  latitude: string | number | null;
  longitude: string | number | null;
  metadata: Record<string, unknown>;
};

export type Reading = {
  id: string;
  device: string;
  device_name: string;
  device_kind: string;
  zone: string | null;
  recorded_at: string;
  soil_moisture: number | null;
  temperature_c: number | null;
  humidity: number | null;
  flow_lpm: number | null;
  rainfall_mm: number | null;
  reservoir_percent: number | null;
};

export type Program = {
  id: string;
  farm: string;
  farm_name: string;
  name: string;
  kind: string;
  season: string;
  seasonal_adjustment_percent: number;
  is_active: boolean;
  notes: string;
  slots: ScheduleSlot[];
};

export type ScheduleSlot = {
  id: string;
  program: string;
  zone: string;
  zone_name: string;
  day_of_week: number;
  start_time: string;
  duration_minutes: number;
  flow_limit_lpm: string | number | null;
  is_active: boolean;
};

export type IrrigationRun = {
  id: string;
  zone: string;
  zone_name: string;
  farm: string;
  farm_name: string;
  source: string;
  status: string;
  planned_minutes: number;
  elapsed_seconds: number;
  volume_m3: string | number | null;
  started_at: string | null;
  notes: string;
};

export type Recommendation = {
  id: string;
  farm: string;
  farm_name: string;
  zone: string;
  zone_name: string;
  title: string;
  rationale: string;
  suggested_minutes: number;
  suggested_volume_m3: string | number;
  confidence: string | number;
  factors: { key: string; label: string; value: number; detail: string }[];
  status: string;
  requires_approval: boolean;
  created_at: string;
};

export type AlertItem = {
  id: string;
  farm_name: string | null;
  zone_name: string | null;
  device_name: string | null;
  kind: string;
  title: string;
  body: string;
  severity: string;
  status: string;
  created_at: string;
};

export type DashboardData = {
  farms: number;
  zones: number;
  devices: number;
  online_devices: number;
  open_alerts: number;
  active_runs: number;
  soil_moisture: number | null;
  flow_lpm: number | null;
  temperature_c: number | null;
  humidity: number | null;
  rainfall_mm: number | null;
  reservoir_percent: number | null;
  volume_24h: number | null;
  cost_24h: number | null;
  weather: { temperature_c: number | null; humidity: number | null; precipitation_mm: number | null; et0_mm: number | null; condition: string | null };
  zone_moisture: { id: string; name: string; moisture: number | null; target_min: number; target_max: number }[];
  usage_trend: { day: string; volume: number; cost: number }[];
  device_mix: { kind: string; count: number }[];
  connectivity: { connectivity: string; count: number }[];
};

export type WaterAnalytics = {
  period_days: number;
  volume: number;
  cost: number;
  efficiency: number;
  previous_volume: number;
  saved_volume: number;
  saving_percent: number;
  by_farm: { id: string; name: string; volume: number; cost: number | null }[];
  by_field: { id: string; name: string; volume: number }[];
  by_zone: { id: string; name: string; volume: number; efficiency: number | null }[];
  by_crop: { name: string; volume: number; cost: number }[];
  history: { day: string; volume: number; cost: number }[];
};

export type Asset = { id: string; farm: string; farm_name: string; name: string; kind: string; serial_number: string; notes: string };
export type WorkOrder = { id: string; asset: string; asset_name: string; farm_name: string; title: string; details: string; status: string; assigned_to_name: string | null; due_on: string | null };
export type WorkTask = { id: string; title: string; details: string; status: string; farm_name: string | null; zone_name: string | null; due_at: string | null };
export type NotificationItem = { id: string; title: string; body: string; kind: string; read_at: string | null; created_at: string; payload: Record<string, unknown> };
export type ReportRun = { id: string; kind: string; status: string; result: { title?: string; rows?: Record<string, unknown>[]; summary?: Record<string, unknown> }; created_at: string };
export type SearchResults = {
  farms: { id: string; label: string; meta: string }[];
  zones: { id: string; label: string; meta: string }[];
  devices: { id: string; label: string; meta: string }[];
  alerts: { id: string; label: string; meta: string }[];
  programs: { id: string; label: string; meta: string }[];
  work_orders: { id: string; label: string; meta: string }[];
};
