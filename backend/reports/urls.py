from django.urls import include, path
from rest_framework.routers import DefaultRouter

from reports.views import ReportCatalogView, ReportExportView, ReportRunViewSet

router = DefaultRouter()
router.register("runs", ReportRunViewSet, basename="report-run")

urlpatterns = [
    path("catalog/", ReportCatalogView.as_view(), name="report-catalog"),
    path("run/", ReportRunViewSet.as_view({"post": "create"}), name="report-run"),
    path("export/", ReportExportView.as_view(), name="report-export"),
    path("", include(router.urls)),
]
