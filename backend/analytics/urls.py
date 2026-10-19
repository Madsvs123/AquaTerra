from django.urls import path

from analytics.views import DashboardView, SnapshotView, WaterAnalyticsView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("water/", WaterAnalyticsView.as_view(), name="water-analytics"),
    path("snapshots/", SnapshotView.as_view(), name="snapshots"),
]
