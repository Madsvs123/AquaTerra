from alerts.models import Alert
from analytics.services import water_analytics
from common.choices import ReportKind
from devices.models import Device
from irrigation.models import WaterUsageRecord
from maintenance.models import WorkOrder


def build_report(organization, kind):
    if kind == ReportKind.WATER_USAGE:
        data = water_analytics(organization, days=30)
        return {"title": "Water usage", "rows": data["history"], "summary": data}
    if kind == ReportKind.ZONE_EFFICIENCY:
        data = water_analytics(organization, days=30)
        return {"title": "Zone efficiency", "rows": data["by_zone"], "summary": data}
    if kind == ReportKind.ALERT_SUMMARY:
        rows = list(Alert.objects.filter(organization=organization).values("kind", "severity", "status")[:200])
        return {"title": "Alert summary", "rows": rows, "count": len(rows)}
    if kind == ReportKind.DEVICE_HEALTH:
        rows = list(Device.objects.filter(organization=organization).values("name", "kind", "health", "connectivity"))
        return {"title": "Device health", "rows": rows}
    if kind == ReportKind.MAINTENANCE:
        rows = list(WorkOrder.objects.filter(organization=organization).values("title", "status", "due_on")[:200])
        return {"title": "Maintenance", "rows": rows}
    if kind == ReportKind.CROP_CONSUMPTION:
        data = water_analytics(organization, days=30)
        return {"title": "Crop consumption", "rows": data["by_crop"]}
    if kind == ReportKind.COST_ESTIMATE:
        data = water_analytics(organization, days=30)
        return {"title": "Cost estimate", "rows": data["by_farm"], "summary": {"cost": data["cost"], "volume": data["volume"]}}
    return {"title": kind, "rows": []}
