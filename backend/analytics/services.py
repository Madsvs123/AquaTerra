from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Sum
from django.utils import timezone

from alerts.models import Alert
from common.choices import AlertStatus, Connectivity, RunStatus
from devices.models import Device, SensorReading
from farms.models import Farm, IrrigationZone
from irrigation.models import IrrigationRun, WaterUsageRecord
from weather.models import WeatherObservation


def dashboard(organization):
    now = timezone.now()
    day_ago = now - timedelta(hours=24)
    zones = IrrigationZone.objects.filter(organization=organization, is_active=True)
    devices = Device.objects.filter(organization=organization, is_active=True)
    moisture = (
        SensorReading.objects.filter(organization=organization, soil_moisture__isnull=False, recorded_at__gte=day_ago)
        .aggregate(avg=Avg("soil_moisture"))
        .get("avg")
    )
    flow = (
        SensorReading.objects.filter(organization=organization, flow_lpm__isnull=False, recorded_at__gte=day_ago)
        .aggregate(avg=Avg("flow_lpm"))
        .get("avg")
    )
    temperature = (
        SensorReading.objects.filter(organization=organization, temperature_c__isnull=False, recorded_at__gte=day_ago)
        .aggregate(avg=Avg("temperature_c"))
        .get("avg")
    )
    humidity = (
        SensorReading.objects.filter(organization=organization, humidity__isnull=False, recorded_at__gte=day_ago)
        .aggregate(avg=Avg("humidity"))
        .get("avg")
    )
    rainfall = (
        SensorReading.objects.filter(organization=organization, rainfall_mm__isnull=False, recorded_at__gte=day_ago)
        .aggregate(total=Sum("rainfall_mm"))
        .get("total")
    )
    reservoir = (
        SensorReading.objects.filter(organization=organization, reservoir_percent__isnull=False)
        .order_by("-recorded_at")
        .values_list("reservoir_percent", flat=True)
        .first()
    )
    usage_24h = WaterUsageRecord.objects.filter(organization=organization, period_start__gte=day_ago).aggregate(
        volume=Sum("volume_m3"), cost=Sum("cost")
    )
    weather = WeatherObservation.objects.filter(organization=organization).order_by("-observed_at").first()
    return {
        "farms": Farm.objects.filter(organization=organization, is_active=True).count(),
        "zones": zones.count(),
        "devices": devices.count(),
        "online_devices": devices.filter(connectivity=Connectivity.ONLINE).count(),
        "open_alerts": Alert.objects.filter(organization=organization, status=AlertStatus.OPEN).count(),
        "active_runs": IrrigationRun.objects.filter(
            organization=organization, status__in=[RunStatus.RUNNING, RunStatus.PAUSED]
        ).count(),
        "soil_moisture": _num(moisture),
        "flow_lpm": _num(flow),
        "temperature_c": _num(temperature),
        "humidity": _num(humidity),
        "rainfall_mm": _num(rainfall),
        "reservoir_percent": _num(reservoir),
        "volume_24h": _num(usage_24h.get("volume")),
        "cost_24h": _num(usage_24h.get("cost")),
        "weather": {
            "temperature_c": _num(weather.temperature_c) if weather else None,
            "humidity": _num(weather.humidity) if weather else None,
            "precipitation_mm": _num(weather.precipitation_mm) if weather else None,
            "et0_mm": _num(weather.et0_mm) if weather else None,
            "condition": weather.condition if weather else None,
        },
        "zone_moisture": zone_moisture_series(organization),
        "usage_trend": usage_trend(organization),
        "device_mix": list(devices.values("kind").annotate(count=Count("id")).order_by("-count")),
        "connectivity": list(devices.values("connectivity").annotate(count=Count("id"))),
    }


def water_analytics(organization, days=14):
    since = timezone.now() - timedelta(days=int(days))
    records = WaterUsageRecord.objects.filter(organization=organization, period_start__gte=since)
    by_farm = list(records.values("farm_id", "farm__name").annotate(volume=Sum("volume_m3"), cost=Sum("cost")))
    by_field = list(records.values("field_id", "field__name").annotate(volume=Sum("volume_m3")))
    by_zone = list(records.values("zone_id", "zone__name").annotate(volume=Sum("volume_m3"), efficiency=Avg("efficiency_percent")))
    by_crop = list(records.values("crop_type").annotate(volume=Sum("volume_m3"), cost=Sum("cost")))
    previous = WaterUsageRecord.objects.filter(
        organization=organization,
        period_start__gte=since - timedelta(days=int(days)),
        period_start__lt=since,
    ).aggregate(volume=Sum("volume_m3"))
    current_volume = records.aggregate(volume=Sum("volume_m3"), cost=Sum("cost"), efficiency=Avg("efficiency_percent"))
    current = float(current_volume.get("volume") or 0)
    prior = float(previous.get("volume") or 0)
    saved = max(prior - current, 0)
    return {
        "period_days": int(days),
        "volume": current,
        "cost": float(current_volume.get("cost") or 0),
        "efficiency": float(current_volume.get("efficiency") or 0),
        "previous_volume": prior,
        "saved_volume": saved,
        "saving_percent": round((saved / prior) * 100, 1) if prior else 0,
        "by_farm": _named(by_farm, "farm__name"),
        "by_field": _named(by_field, "field__name"),
        "by_zone": _named(by_zone, "zone__name"),
        "by_crop": [
            {"name": row["crop_type"] or "unknown", "volume": float(row["volume"] or 0), "cost": float(row.get("cost") or 0)}
            for row in by_crop
        ],
        "history": usage_trend(organization, days=int(days)),
    }


def zone_moisture_series(organization):
    rows = []
    for zone in IrrigationZone.objects.filter(organization=organization, is_active=True)[:12]:
        reading = SensorReading.objects.filter(zone=zone, soil_moisture__isnull=False).order_by("-recorded_at").first()
        rows.append(
            {
                "id": str(zone.id),
                "name": zone.name,
                "moisture": float(reading.soil_moisture) if reading and reading.soil_moisture is not None else None,
                "target_min": float(zone.target_moisture_min),
                "target_max": float(zone.target_moisture_max),
            }
        )
    return rows


def usage_trend(organization, days=14):
    since = timezone.now() - timedelta(days=days)
    rows = (
        WaterUsageRecord.objects.filter(organization=organization, period_start__gte=since)
        .extra(select={"day": "date(period_start)"})
        .values("day")
        .annotate(volume=Sum("volume_m3"), cost=Sum("cost"))
        .order_by("day")
    )
    return [{"day": str(row["day"]), "volume": float(row["volume"] or 0), "cost": float(row["cost"] or 0)} for row in rows]


def _named(rows, name_key):
    return [
        {
            "id": str(row.get("farm_id") or row.get("field_id") or row.get("zone_id") or ""),
            "name": row.get(name_key) or "Unassigned",
            "volume": float(row.get("volume") or 0),
            "cost": float(row.get("cost") or 0) if "cost" in row else None,
            "efficiency": float(row["efficiency"]) if row.get("efficiency") is not None else None,
        }
        for row in rows
    ]


def _num(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return float(value)
