from rest_framework import serializers

from devices.models import Device, DeviceHealthEvent, SensorReading


class DeviceSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source="farm.name", read_only=True)
    zone_name = serializers.CharField(source="zone.name", read_only=True)

    class Meta:
        model = Device
        fields = [
            "id",
            "farm",
            "farm_name",
            "zone",
            "zone_name",
            "name",
            "serial_number",
            "kind",
            "manufacturer",
            "model_name",
            "firmware",
            "latitude",
            "longitude",
            "connectivity",
            "health",
            "battery_percent",
            "last_seen_at",
            "last_error",
            "metadata",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "connectivity", "health", "last_seen_at", "created_at", "updated_at"]


class SensorReadingSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True)
    device_kind = serializers.CharField(source="device.kind", read_only=True)

    class Meta:
        model = SensorReading
        fields = [
            "id",
            "device",
            "device_name",
            "device_kind",
            "zone",
            "recorded_at",
            "soil_moisture",
            "temperature_c",
            "humidity",
            "flow_lpm",
            "rainfall_mm",
            "reservoir_percent",
            "pressure_bar",
            "payload",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class DeviceHealthEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceHealthEvent
        fields = ["id", "device", "health", "connectivity", "message", "battery_percent", "created_at"]
        read_only_fields = ["id", "created_at"]
