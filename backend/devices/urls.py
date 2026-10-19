from django.urls import include, path
from rest_framework.routers import DefaultRouter

from devices.views import DeviceIngestView, DeviceViewSet, SensorReadingViewSet

router = DefaultRouter()
router.register("inventory", DeviceViewSet, basename="device")
router.register("readings", SensorReadingViewSet, basename="reading")

urlpatterns = [
    path("ingest/", DeviceIngestView.as_view(), name="device-ingest"),
    path("", include(router.urls)),
]
