from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins import FarmScopeMixin, PermissionMixin
from devices.models import Device, DeviceHealthEvent, SensorReading
from devices.serializers import DeviceHealthEventSerializer, DeviceSerializer, SensorReadingSerializer
from devices.services import ingest_reading


class DeviceViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = Device.objects.select_related("farm", "zone")
    serializer_class = DeviceSerializer
    required_permission = "devices.write"
    required_read_permission = "devices.read"
    search_fields = ["name", "serial_number", "kind"]
    filterset_fields = ["farm", "zone", "kind", "connectivity", "health", "is_active"]
    farm_lookups = ("farm",)
    zone_lookups = ("zone",)

    @action(detail=True, methods=["get"])
    def readings(self, request, pk=None):
        device = self.get_object()
        qs = device.readings.all()[:200]
        return Response(SensorReadingSerializer(qs, many=True).data)

    @action(detail=True, methods=["get"])
    def health_log(self, request, pk=None):
        device = self.get_object()
        return Response(DeviceHealthEventSerializer(device.health_events.all()[:50], many=True).data)


class SensorReadingViewSet(FarmScopeMixin, PermissionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = SensorReading.objects.select_related("device", "zone")
    serializer_class = SensorReadingSerializer
    required_read_permission = "devices.read"
    filterset_fields = ["device", "zone"]
    farm_lookups = ("device__farm",)
    zone_lookups = ("zone",)

    def get_queryset(self):
        qs = super().get_queryset()
        since = self.request.query_params.get("since")
        if since:
            qs = qs.filter(recorded_at__gte=since)
        return qs


class DeviceIngestView(APIView):
    required_permission = "devices.write"

    def post(self, request):
        serial = request.data.get("serial_number")
        device = Device.objects.filter(organization=request.organization, serial_number=serial).first()
        if not device:
            return Response({"detail": "Unknown device serial."}, status=404)
        reading = ingest_reading(
            organization=request.organization,
            device=device,
            recorded_at=request.data.get("recorded_at") or timezone.now(),
            soil_moisture=request.data.get("soil_moisture"),
            temperature_c=request.data.get("temperature_c"),
            humidity=request.data.get("humidity"),
            flow_lpm=request.data.get("flow_lpm"),
            rainfall_mm=request.data.get("rainfall_mm"),
            reservoir_percent=request.data.get("reservoir_percent"),
            pressure_bar=request.data.get("pressure_bar"),
            battery_percent=request.data.get("battery_percent"),
            payload=request.data.get("payload") or {},
        )
        return Response(SensorReadingSerializer(reading).data, status=201)
