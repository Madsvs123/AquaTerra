from datetime import timedelta

from django.utils import timezone

from alerts.models import Alert, AlertRule
from common.choices import AlertKind, AlertStatus, Connectivity, DeviceHealth
from devices.models import Device, SensorReading
from farms.models import IrrigationZone
from irrigation.models import IrrigationRun
from notifications.services import notify_operators


def evaluate_organization(organization):
    rules = AlertRule.objects.filter(organization=organization, is_active=True)
    created = []
    for rule in rules:
        created.extend(evaluate_rule(organization, rule))
    return created


def evaluate_rule(organization, rule):
    created = []
    if rule.kind == AlertKind.LOW_SOIL_MOISTURE:
        created += _low_moisture(organization, rule)
    elif rule.kind == AlertKind.EXCESSIVE_WATERING:
        created += _excessive_watering(organization, rule)
    elif rule.kind in {AlertKind.LEAK, AlertKind.UNUSUAL_FLOW}:
        created += _flow_anomalies(organization, rule)
    elif rule.kind == AlertKind.SENSOR_FAILURE:
        created += _sensor_failures(organization, rule)
    elif rule.kind == AlertKind.LOW_RESERVOIR:
        created += _low_reservoir(organization, rule)
    elif rule.kind == AlertKind.PUMP_FAULT:
        created += _pump_faults(organization, rule)
    elif rule.kind == AlertKind.DISCONNECTED_DEVICE:
        created += _disconnected(organization, rule)
    return created


def _open_exists(organization, kind, **filters):
    return Alert.objects.filter(organization=organization, kind=kind, status=AlertStatus.OPEN, **filters).exists()


def _raise(organization, rule, title, body, **kwargs):
    alert = Alert.objects.create(
        organization=organization,
        rule=rule,
        kind=rule.kind,
        title=title,
        body=body,
        severity=rule.severity,
        **kwargs,
    )
    notify_operators(organization, title=title, body=body, kind="alert", payload={"alert_id": str(alert.id)})
    return alert


def _low_moisture(organization, rule):
    created = []
    zones = IrrigationZone.objects.filter(organization=organization, is_active=True)
    if rule.zone_id:
        zones = zones.filter(id=rule.zone_id)
    if rule.farm_id:
        zones = zones.filter(farm_id=rule.farm_id)
    for zone in zones:
        reading = SensorReading.objects.filter(zone=zone, soil_moisture__isnull=False).order_by("-recorded_at").first()
        if not reading:
            continue
        if float(reading.soil_moisture) >= float(zone.target_moisture_min):
            continue
        if _open_exists(organization, rule.kind, zone=zone):
            continue
        created.append(
            _raise(
                organization,
                rule,
                f"Low soil moisture in {zone.name}",
                f"Latest reading is {reading.soil_moisture}% against a {zone.target_moisture_min}% floor.",
                farm=zone.farm,
                zone=zone,
                payload={"soil_moisture": float(reading.soil_moisture)},
            )
        )
    return created


def _excessive_watering(organization, rule):
    created = []
    percent = float((rule.threshold or {}).get("percent", 125))
    since = timezone.now() - timedelta(hours=24)
    for zone in IrrigationZone.objects.filter(organization=organization, is_active=True):
        volume = sum(float(run.volume_m3 or 0) for run in IrrigationRun.objects.filter(zone=zone, ended_at__gte=since))
        expected = float(zone.flow_limit_lpm or 30) * 0.04
        if expected and volume > expected * (percent / 100) and not _open_exists(organization, rule.kind, zone=zone):
            created.append(
                _raise(
                    organization,
                    rule,
                    f"Excessive watering in {zone.name}",
                    f"{volume:.2f} m³ used in 24h versus a {expected:.2f} m³ typical budget.",
                    farm=zone.farm,
                    zone=zone,
                    payload={"volume_m3": volume},
                )
            )
    return created


def _flow_anomalies(organization, rule):
    created = []
    multiplier = float((rule.threshold or {}).get("flow_multiplier", 1.8))
    for zone in IrrigationZone.objects.filter(organization=organization, is_active=True):
        reading = SensorReading.objects.filter(zone=zone, flow_lpm__isnull=False).order_by("-recorded_at").first()
        if not reading:
            continue
        limit = float(zone.flow_limit_lpm or 40)
        if float(reading.flow_lpm) <= limit * multiplier:
            continue
        if _open_exists(organization, rule.kind, zone=zone):
            continue
        title = f"{'Possible leak' if rule.kind == AlertKind.LEAK else 'Unusual flow'} in {zone.name}"
        created.append(
            _raise(
                organization,
                rule,
                title,
                f"Flow is {reading.flow_lpm} L/min against a {limit} L/min limit.",
                farm=zone.farm,
                zone=zone,
                payload={"flow_lpm": float(reading.flow_lpm)},
            )
        )
    return created


def _sensor_failures(organization, rule):
    created = []
    stale_minutes = int((rule.threshold or {}).get("stale_minutes", 30))
    cutoff = timezone.now() - timedelta(minutes=stale_minutes)
    devices = Device.objects.filter(organization=organization, is_active=True, kind__in=["soil_moisture", "temperature", "humidity", "flow_meter"])
    for device in devices:
        if device.last_seen_at and device.last_seen_at >= cutoff and device.health != DeviceHealth.FAULT:
            continue
        if _open_exists(organization, rule.kind, device=device):
            continue
        created.append(
            _raise(
                organization,
                rule,
                f"Sensor failure: {device.name}",
                device.last_error or "Sensor has stopped reporting valid telemetry.",
                farm=device.farm,
                zone=device.zone,
                device=device,
            )
        )
    return created


def _low_reservoir(organization, rule):
    created = []
    percent = float((rule.threshold or {}).get("percent", 20))
    reading = SensorReading.objects.filter(organization=organization, reservoir_percent__isnull=False).order_by("-recorded_at").first()
    if not reading or float(reading.reservoir_percent) > percent:
        return created
    if _open_exists(organization, rule.kind, device=reading.device):
        return created
    created.append(
        _raise(
            organization,
            rule,
            "Reservoir level is low",
            f"Reservoir is at {reading.reservoir_percent}%.",
            farm=reading.device.farm if reading.device else None,
            device=reading.device,
            payload={"reservoir_percent": float(reading.reservoir_percent)},
        )
    )
    return created


def _pump_faults(organization, rule):
    created = []
    pumps = Device.objects.filter(organization=organization, kind="pump", health=DeviceHealth.FAULT)
    for pump in pumps:
        if _open_exists(organization, rule.kind, device=pump):
            continue
        created.append(
            _raise(
                organization,
                rule,
                f"Pump fault: {pump.name}",
                pump.last_error or "Controller reported a pump fault.",
                farm=pump.farm,
                zone=pump.zone,
                device=pump,
            )
        )
    return created


def _disconnected(organization, rule):
    created = []
    devices = Device.objects.filter(organization=organization, is_active=True, connectivity=Connectivity.OFFLINE)
    for device in devices:
        if _open_exists(organization, rule.kind, device=device):
            continue
        created.append(
            _raise(
                organization,
                rule,
                f"Disconnected: {device.name}",
                "Device is offline and has not reported recently.",
                farm=device.farm,
                zone=device.zone,
                device=device,
            )
        )
    return created
