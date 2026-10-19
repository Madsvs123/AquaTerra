from rest_framework import viewsets

from common.mixins import FarmScopeMixin, PermissionMixin
from maintenance.models import Asset, Inspection, ServiceSchedule, WorkOrder
from maintenance.serializers import (
    AssetSerializer,
    InspectionSerializer,
    ServiceScheduleSerializer,
    WorkOrderSerializer,
)


class AssetViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = Asset.objects.select_related("farm", "zone", "device")
    serializer_class = AssetSerializer
    required_permission = "maintenance.write"
    required_read_permission = "maintenance.read"
    search_fields = ["name", "serial_number"]
    filterset_fields = ["farm", "kind"]
    farm_lookups = ("farm",)
    zone_lookups = ("zone",)


class ServiceScheduleViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = ServiceSchedule.objects.select_related("asset", "assigned_to")
    serializer_class = ServiceScheduleSerializer
    required_permission = "maintenance.write"
    required_read_permission = "maintenance.read"
    filterset_fields = ["asset", "is_active"]
    farm_lookups = ("asset__farm",)
    zone_lookups = ("asset__zone",)


class InspectionViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = Inspection.objects.select_related("asset", "inspected_by")
    serializer_class = InspectionSerializer
    required_permission = "maintenance.write"
    required_read_permission = "maintenance.read"
    filterset_fields = ["asset", "result"]
    farm_lookups = ("asset__farm",)
    zone_lookups = ("asset__zone",)

    def perform_create(self, serializer):
        org = self.request.organization
        extra = {"inspected_by": self.request.user}
        serializer.save(organization=org, **extra)


class WorkOrderViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = WorkOrder.objects.select_related("asset", "farm", "assigned_to")
    serializer_class = WorkOrderSerializer
    required_permission = "maintenance.write"
    required_read_permission = "maintenance.read"
    search_fields = ["title", "details"]
    filterset_fields = ["farm", "status", "assigned_to"]
    farm_lookups = ("farm",)
    zone_lookups = ("asset__zone",)
