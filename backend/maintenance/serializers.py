from rest_framework import serializers

from maintenance.models import Asset, Inspection, ServiceSchedule, WorkOrder


class AssetSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source="farm.name", read_only=True)

    class Meta:
        model = Asset
        fields = [
            "id",
            "farm",
            "farm_name",
            "zone",
            "device",
            "name",
            "kind",
            "installed_on",
            "serial_number",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ServiceScheduleSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source="asset.name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)

    class Meta:
        model = ServiceSchedule
        fields = [
            "id",
            "asset",
            "asset_name",
            "title",
            "interval_days",
            "next_due_on",
            "assigned_to",
            "assigned_to_name",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InspectionSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source="asset.name", read_only=True)

    class Meta:
        model = Inspection
        fields = ["id", "asset", "asset_name", "inspected_by", "inspected_on", "result", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class WorkOrderSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source="asset.name", read_only=True)
    farm_name = serializers.CharField(source="farm.name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            "id",
            "asset",
            "asset_name",
            "farm",
            "farm_name",
            "title",
            "details",
            "status",
            "assigned_to",
            "assigned_to_name",
            "due_on",
            "completed_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
