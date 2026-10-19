import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell, ProtectedRoute } from "@/components/layout/AppShell";
import LoginPage from "@/pages/auth/LoginPage";
import RegisterPage from "@/pages/auth/RegisterPage";
import InvitePage from "@/pages/auth/InvitePage";
import DashboardPage from "@/pages/dashboard/DashboardPage";
import MapPage from "@/pages/map/MapPage";
import FarmsPage from "@/pages/farms/FarmsPage";
import FarmDetailPage from "@/pages/farms/FarmDetailPage";
import ZonesPage from "@/pages/zones/ZonesPage";
import ZoneDetailPage from "@/pages/zones/ZoneDetailPage";
import DevicesPage from "@/pages/devices/DevicesPage";
import DeviceDetailPage from "@/pages/devices/DeviceDetailPage";
import SchedulesPage from "@/pages/schedules/SchedulesPage";
import ControlPage from "@/pages/control/ControlPage";
import RecommendationsPage from "@/pages/recommendations/RecommendationsPage";
import AlertsPage from "@/pages/alerts/AlertsPage";
import AnalyticsPage from "@/pages/analytics/AnalyticsPage";
import MaintenancePage from "@/pages/maintenance/MaintenancePage";
import TasksPage from "@/pages/tasks/TasksPage";
import ReportsPage from "@/pages/reports/ReportsPage";
import NotificationsPage from "@/pages/notifications/NotificationsPage";
import SearchPage from "@/pages/search/SearchPage";
import SettingsPage from "@/pages/settings/SettingsPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/invite/:token" element={<InvitePage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/map" element={<MapPage /} />
          <Route path="/farms" element={<FarmsPage />} />
          <Route path="/farms/:id" element={<FarmDetailPage />} />
          <Route path="/zones" element={<ZonesPage />} />
          <Route path="/zones/:id" element={<ZoneDetailPage />} />
          <Route path="/devices" element={<DevicesPage />} />
          <Route path="/devices/:id" element={<DeviceDetailPage />} />
          <Route path="/schedules" element={<SchedulesPage />} />
          <Route path="/control" element={<ControlPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/maintenance" element={<MaintenancePage />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/settings" element={<SearchPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  ));
}
