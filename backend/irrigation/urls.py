from django.urls import include, path
from rest_framework.routers import DefaultRouter

from irrigation.views import (
    ActiveIrrigationView,
    IrrigationProgramViewSet,
    IrrigationRunViewSet,
    ManualWateringView,
    ScheduleSlotViewSet,
    WaterUsageViewSet,
)

router = DefaultRouter()
router.register("programs", IrrigationProgramViewSet, basename="program")
router.register("slots", ScheduleSlotViewSet, basename="slot")
router.register("runs", IrrigationRunViewSet, basename="run")
router.register("usage", WaterUsageViewSet, basename="usage")

urlpatterns = [
    path("manual/", ManualWateringView.as_view(), name="manual-watering"),
    path("active/", ActiveIrrigationView.as_view(), name="active-irrigation"),
    path("", include(router.urls)),
]
