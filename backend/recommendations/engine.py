from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from common.choices import RecommendationStatus, RunStatus
from devices.models import SensorReading
from farms.models import IrrigationZone
from irrigation.models import IrrigationRun
from recommendations.models import Recommendation
from weather.models import WeatherObservation

CROP_WATER_NEED = {
    "tomato": 28,
    "lettuce": 22,
    "corn": 32,
    "wheat": 24,
    "citrus": 26,
    "grape": 20,
    "olive": 16,
    "alfalfa": 34,
    "berry": 27,
    "turf": 30,
    "ornamental": 18,
    "mixed": 24,
}

SOIL_HOLDING = {
    "sand": 0.7,
    "sandy_loam": 0.85,
    "loam": 1.0,
    "silt": 1.05,
    "clay_loam": 1.1,
    "clay": 1.2,
    "peat": 1.3,
    "chalk": 0.8,
}


def generate_for_organization(organization):
    created = []
    settings = organization.settings or {}
    require_approval = bool(settings.get("require_recommendation_approval", True))
    zones = IrrigationZone.objects.select_related("farm", "field").filter(organization=organization, is_active=True)
    for zone in zones:
        rec = evaluate_zone(organization, zone, require_approval)
        if rec:
            created.append(rec)
    return created


def evaluate_zone(organization, zone, require_approval):
    if Recommendation.objects.filter(
        organization=organization, zone=zone, status=RecommendationStatus.PENDING
    ).exists():
        return None
    if IrrigationRun.objects.filter(
        organization=organization, zone=zone, status__in=[RunStatus.RUNNING, RunStatus.PAUSED, RunStatus.QUEUED]
    ).exists():
        return None

    latest = (
        SensorReading.objects.filter(organization=organization, zone=zone, soil_moisture__isnull=False)
        .order_by("-recorded_at")
        .first()
    )
    if not latest or latest.soil_moisture is None:
        return None

    moisture = float(latest.soil_moisture)
    target_min = float(zone.target_moisture_min)
    buffer = float((organization.settings or {}).get("low_moisture_buffer", 2))
    if moisture >= target_min - buffer:
        return None

    weather = (
        WeatherObservation.objects.filter(organization=organization, farm=zone.farm)
        .order_by("-observed_at")
        .first()
    )
    rainfall = float(weather.precipitation_mm) if weather and weather.precipitation_mm is not None else 0
    et0 = float(weather.et0_mm) if weather and weather.et0_mm is not None else 4.2
    if rainfall >= 8:
        return None

    crop_need = CROP_WATER_NEED.get(zone.field.crop_type, 24)
    soil = SOIL_HOLDING.get(zone.field.soil_type, 1.0)
    deficit = max(target_min - moisture, 0)
    minutes = int(max(8, min(90, (deficit * crop_need * soil) / 6 + et0 * 3)))
    volume = Decimal(str(zone.flow_limit_lpm or 30)) * Decimal(minutes) / Decimal("1000")
    confidence = min(96, 58 + deficit * 3 + (4 if weather else 0))
    factors = [
        {"key": "soil_moisture", "label": "Current moisture", "value": moisture, "detail": f"{moisture:.1f}% vs {target_min:.1f}% target"},
        {"key": "crop", "label": "Crop demand", "value": crop_need, "detail": zone.field.crop_type.replace("_", " ")},
        {"key": "soil", "label": "Soil holding", "value": soil, "detail": zone.field.soil_type.replace("_", " ")},
        {"key": "rainfall", "label": "Recent rainfall", "value": rainfall, "detail": f"{rainfall:.1f} mm"},
        {"key": "et0", "label": "Evapotranspiration", "value": et0, "detail": f"{et0:.1f} mm"},
    ]
    needs_approval = require_approval and zone.require_recommendation_approval
    return Recommendation.objects.create(
        organization=organization,
        farm=zone.farm,
        zone=zone,
        title=f"Irrigate {zone.name} for {minutes} minutes",
        rationale=(
            f"{zone.name} is {deficit:.1f} points below the moisture floor. "
            f"Crop demand and current weather support a {minutes}-minute cycle."
        ),
        suggested_minutes=minutes,
        suggested_volume_m3=volume.quantize(Decimal("0.001")),
        confidence=Decimal(str(round(confidence, 2))),
        factors=factors,
        status=RecommendationStatus.PENDING,
        requires_approval=needs_approval,
        expires_at=timezone.now() + timedelta(hours=8),
    )
