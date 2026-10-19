from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from common.choices import RunSource, RunStatus
from common.mixins import FarmScopeMixin, PermissionMixin
from farms.models import IrrigationZone
from irrigation.models import IrrigationProgram, IrrigationRun, ScheduleSlot, WaterUsageRecord
from irrigation.serializers import (
    IrrigationProgramSerializer,
    IrrigationRunSerializer,
    ScheduleSlotSerializer,
    WaterUsageRecordSerializer,
)
from irrigation.services import pause_run, resume_run, start_run, stop_run


class IrrigationProgramViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = IrrigationProgram.objects.select_related("farm").prefetch_related("slots__zone")
    serializer_class = IrrigationProgramSerializer
    required_permission = "irrigation.control"
    required_read_permission = "irrigation.read"
    search_fields = ["name"]
    filterset_fields = ["farm", "kind", "is_active"]
    farm_lookups = ("farm",)
    zone_lookups = ("slots__zone",)


class ScheduleSlotViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = ScheduleSlot.objects.select_related("program", "zone")
    serializer_class = ScheduleSlotSerializer
    required_permission = "irrigation.control"
    required_read_permission = "irrigation.read"
    filterset_fields = ["program", "zone", "day_of_week", "is_active"]
    farm_lookups = ("zone__farm",)
    zone_lookups = ("zone",)


class IrrigationRunViewSet(FarmScopeMixin, PermissionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = IrrigationRun.objects.select_related("zone", "farm", "requested_by")
    serializer_class = IrrigationRunSerializer
    required_read_permission = "irrigation.read"
    filterset_fields = ["farm", "zone", "status", "source"]
    farm_lookups = ("farm",)
    zone_lookups = ("zone",)

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        self.check_action_permission("irrigation.control")
        return Response(IrrigationRunSerializer(pause_run(self.get_object())).data)

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        self.check_action_permission("irrigation.control")
        return Response(IrrigationRunSerializer(resume_run(self.get_object())).data)

    @action(detail=True, methods=["post"])
    def stop(self, request, pk=None):
        self.check_action_permission("irrigation.control")
        status = request.data.get("status") or RunStatus.COMPLETED
        return Response(IrrigationRunSerializer(stop_run(self.get_object(), status=status)).data)


class ManualWateringView(APIView):
    required_permission = "irrigation.control"

    def post(self, request):
        zone = IrrigationZone.objects.filter(organization=request.organization, id=request.data.get("zone")).first()
        if not zone:
            return Response({"detail": "Zone not found."}, status=404)
        minutes = int(request.data.get("minutes") or 15)
        run = start_run(
            organization=request.organization,
            zone=zone,
            user=request.user,
            source=RunSource.MANUAL,
            minutes=minutes,
            notes=request.data.get("notes") or "Manual watering",
        )
        return Response(IrrigationRunSerializer(run).data, status=201)


class ActiveIrrigationView(APIView):
    required_read_permission = "irrigation.read"

    def get(self, request):
        qs = IrrigationRun.objects.select_related("zone", "farm").filter(
            organization=request.organization,
            status__in=[RunStatus.RUNNING, RunStatus.PAUSED, RunStatus.QUEUED],
        )
        return Response(IrrigationRunSerializer(qs, many=True).data)


class WaterUsageViewSet(FarmScopeMixin, PermissionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = WaterUsageRecord.objects.select_related("farm", "zone", "field")
    serializer_class = WaterUsageRecordSerializer
    required_read_permission = "analytics.read"
    filterset_fields = ["farm", "zone", "field", "crop_type"]
    farm_lookups = ("farm",)
    zone_lookups = ("zone",)
