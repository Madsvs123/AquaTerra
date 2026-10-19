from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from common.choices import Connectivity, DeviceHealth
from devices.models import DeviceHealthEvent, SensorReading


def ingest_reading(*, organization, device, recorded_at=None, **metrics):
    reading = SensorReading.objects.create(
        organization=organization,
        device=device,
        zone=device.zone,
        recorded_at=recorded_at or timezone.now(),
        soil_moisture=metrics.get("soil_moisture"),
        temperature_c=metrics.get("temperature_c"),
        humidity=metrics.get("humidity"),
        flow_lpm=metrics.get("flow_lpm"),
        rainfall_mm=metrics.get("rainfall_mm"),
        reservoir_percent=metrics.get("reservoir_percent"),
        pressure_bar=metrics.get("pressure_bar"),
        payload=metrics.get("payload") or {},
    )
    device.last_seen_at = reading.recorded_at
    device.connectivity = Connectivity.ONLINE
    if metrics.get("battery_percent") is not None:
        device.battery_percent = metrics["battery_percent"]
    if device.health == DeviceHealth.OFFLINE:
        device.health = DeviceHealth.HEALTHY
        DeviceHealthEvent.objects.create(
            organization=organization,
            device=device,
            health=device.health,
            connectivity=device.connectivity,
            message="Device resumed telemetry",
            battery_percent=device.battery_percent,
        )
    device.save(
        update_fields=["last_seen_at", "connectivity", "battery_percent", "health", "updated_at"]
    )
    publish_telemetry(organization.id, reading)
    return reading


def publish_telemetry(organization_id, reading):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    payload = {
        "type": "telemetry",
        "payload": {
            "id": str(reading.id),
            "device": str(reading.device_id),
            "zone": str(reading.zone_id) if reading.zone_id else None,
            "recorded_at": reading.recorded_at.isoformat(),
            "soil_moisture": _num(reading.soil_moisture),
            "temperature_c": _num(reading.temperature_c),
            "humidity": _num(reading.humidity),
            "flow_lpm": _num(reading.flow_lpm),
            "rainfall_mm": _num(reading.rainfall_mm),
            "reservoir_percent": _num(reading.reservoir_percent),
        },
    }
    try:
        async_to_sync(channel_layer.group_send)(f"org_{organization_id}_telemetry", payload)
    except Exception:
        pass


def _num(value):
    return float(value) if value is not None else None
