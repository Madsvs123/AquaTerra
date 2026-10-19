from rest_framework import serializers

from irrigation.models import IrrigationProgram, IrrigationRun, ScheduleSlot, WaterUsageRecord


class ScheduleSlotSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source="zone.name", read_only=True)

    class Meta:
        model = ScheduleSlot
        fields = [
            "id",
            "program",
            "zone",
            "zone_name",
            "day_of_week",
            "start_time",
            "duration_minutes",
            "flow_limit_lpm",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class IrrigationProgramSerializer(serializers.ModelSerializer):
    slots = ScheduleSlotSerializer(many=True, read_only=True)
    farm_name = serializers.CharField(source="farm.name", read_only=True)

    class Meta:
        model = IrrigationProgram
        fields = [
            "id",
            "farm",
            "farm_name",
            "name",
            "kind",
            "season",
            "seasonal_adjustment_percent",
            "is_active",
            "notes",
            "slots",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class IrrigationRunSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    farm_name = serializers.CharField(source="farm.name", read_only=True)
    requested_by_name = serializers.CharField(source="requested_by.full_name", read_only=True)

    class Meta:
        model = IrrigationRun
        fields = [
            "id",
            "zone",
            "zone_name",
            "farm",
            "farm_name",
            "program",
            "slot",
            "recommendation",
            "source",
            "status",
            "requested_by",
            "requested_by_name",
            "scheduled_for",
            "started_at",
            "paused_at",
            "ended_at",
            "planned_minutes",
            "elapsed_seconds",
            "volume_m3",
            "peak_flow_lpm",
            "notes",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "started_at",
            "paused_at",
            "ended_at",
            "elapsed_seconds",
            "volume_m3",
            "created_at",
        ]


class WaterUsageRecordSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    farm_name = serializers.CharField(source="farm.name", read_only=True)

    class Meta:
        model = WaterUsageRecord
        fields = [
            "id",
            "farm",
            "farm_name",
            "field",
            "zone",
            "zone_name",
            "crop_type",
            "run",
            "period_start",
            "period_end",
            "volume_m3",
            "cost",
            "efficiency_percent",
        ]
