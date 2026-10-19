from rest_framework import serializers

from alerts.models import Alert, AlertRule


class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = [
            "id",
            "farm",
            "zone",
            "name",
            "kind",
            "severity",
            "threshold",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AlertSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source="farm.name", read_only=True)
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    device_name = serializers.CharField(source="device.name", read_only=True)

    class Meta:
        model = Alert
        fields = [
            "id",
            "rule",
            "farm",
            "farm_name",
            "zone",
            "zone_name",
            "device",
            "device_name",
            "kind",
            "title",
            "body",
            "severity",
            "status",
            "acknowledged_by",
            "resolved_at",
            "payload",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
