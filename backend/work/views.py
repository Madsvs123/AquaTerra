from rest_framework import serializers, viewsets

from common.mixins import FarmScopeMixin, PermissionMixin
from work.models import WorkTask


class WorkTaskSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source="farm.name", read_only=True)
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)

    class Meta:
        model = WorkTask
        fields = [
            "id",
            "farm",
            "farm_name",
            "zone",
            "zone_name",
            "title",
            "details",
            "status",
            "assigned_to",
            "assigned_to_name",
            "due_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class WorkTaskViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = WorkTask.objects.select_related("farm", "zone", "assigned_to")
    serializer_class = WorkTaskSerializer
    required_permission = "tasks.write"
    required_read_permission = "tasks.read"
    search_fields = ["title", "details"]
    filterset_fields = ["status", "farm", "assigned_to"]
    farm_lookups = ("farm",)
    zone_lookups = ("zone",)
