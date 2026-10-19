from django.urls import include, path
from rest_framework.routers import DefaultRouter

from maintenance.views import AssetViewSet, InspectionViewSet, ServiceScheduleViewSet, WorkOrderViewSet

router = DefaultRouter()
router.register("assets", AssetViewSet, basename="asset")
router.register("schedules", ServiceScheduleViewSet, basename="service-schedule")
router.register("inspections", InspectionViewSet, basename="inspection")
router.register("work-orders", WorkOrderViewSet, basename="work-order")

urlpatterns = [path("", include(router.urls))]
