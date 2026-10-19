class SystemRole:
    OWNER = "owner"
    ADMIN = "admin"
    AGRONOMIST = "agronomist"
    OPERATOR = "operator"
    TECHNICIAN = "technician"
    VIEWER = "viewer"

    CHOICES = [
        (OWNER, "Owner"),
        (ADMIN, "Admin"),
        (AGRONOMIST, "Agronomist"),
        (OPERATOR, "Irrigation operator"),
        (TECHNICIAN, "Technician"),
        (VIEWER, "Viewer"),
    ]


ALL_PERMISSIONS = [
    "farms.read",
    "farms.write",
    "zones.read",
    "zones.write",
    "devices.read",
    "devices.write",
    "irrigation.read",
    "irrigation.control",
    "recommendations.read",
    "recommendations.approve",
    "alerts.read",
    "alerts.write",
    "analytics.read",
    "maintenance.read",
    "maintenance.write",
    "tasks.read",
    "tasks.write",
    "reports.read",
    "reports.export",
    "weather.read",
    "settings.manage",
    "members.manage",
    "apikeys.manage",
    "audit.read",
]


ROLE_PERMISSIONS = {
    SystemRole.OWNER: {"*"},
    SystemRole.ADMIN: set(ALL_PERMISSIONS),
    SystemRole.AGRONOMIST: {
        "farms.read",
        "farms.write",
        "zones.read",
        "zones.write",
        "devices.read",
        "irrigation.read",
        "recommendations.read",
        "recommendations.approve",
        "alerts.read",
        "alerts.write",
        "analytics.read",
        "maintenance.read",
        "tasks.read",
        "tasks.write",
        "reports.read",
        "reports.export",
        "weather.read",
    },
    SystemRole.OPERATOR: {
        "farms.read",
        "zones.read",
        "devices.read",
        "irrigation.read",
        "irrigation.control",
        "recommendations.read",
        "alerts.read",
        "analytics.read",
        "maintenance.read",
        "tasks.read",
        "tasks.write",
        "reports.read",
        "weather.read",
    },
    SystemRole.TECHNICIAN: {
        "farms.read",
        "zones.read",
        "devices.read",
        "devices.write",
        "irrigation.read",
        "alerts.read",
        "alerts.write",
        "maintenance.read",
        "maintenance.write",
        "tasks.read",
        "tasks.write",
        "weather.read",
    },
    SystemRole.VIEWER: {
        "farms.read",
        "zones.read",
        "devices.read",
        "irrigation.read",
        "recommendations.read",
        "alerts.read",
        "analytics.read",
        "maintenance.read",
        "tasks.read",
        "reports.read",
        "weather.read",
    },
}


class InvitationStatus:
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"

    CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (EXPIRED, "Expired"),
        (REVOKED, "Revoked"),
    ]


class CropType:
    TOMATO = "tomato"
    LETTUCE = "lettuce"
    CORN = "corn"
    WHEAT = "wheat"
    CITRUS = "citrus"
    GRAPE = "grape"
    OLIVE = "olive"
    ALFALFA = "alfalfa"
    BERRY = "berry"
    TURF = "turf"
    ORNAMENTAL = "ornamental"
    MIXED = "mixed"

    CHOICES = [
        (TOMATO, "Tomato"),
        (LETTUCE, "Lettuce"),
        (CORN, "Corn"),
        (WHEAT, "Wheat"),
        (CITRUS, "Citrus"),
        (GRAPE, "Grape"),
        (OLIVE, "Olive"),
        (ALFALFA, "Alfalfa"),
        (BERRY, "Berry"),
        (TURF, "Turf"),
        (ORNAMENTAL, "Ornamental"),
        (MIXED, "Mixed"),
    ]


class SoilType:
    SAND = "sand"
    LOAM = "loam"
    CLAY = "clay"
    SILT = "silt"
    PEAT = "peat"
    CHALK = "chalk"
    SANDY_LOAM = "sandy_loam"
    CLAY_LOAM = "clay_loam"

    CHOICES = [
        (SAND, "Sand"),
        (LOAM, "Loam"),
        (CLAY, "Clay"),
        (SILT, "Silt"),
        (PEAT, "Peat"),
        (CHALK, "Chalk"),
        (SANDY_LOAM, "Sandy loam"),
        (CLAY_LOAM, "Clay loam"),
    ]


class IrrigationMethod:
    DRIP = "drip"
    SPRINKLER = "sprinkler"
    MICRO_SPRAY = "micro_spray"
    FLOOD = "flood"
    PIVOT = "pivot"
    SUBSURFACE = "subsurface"
    HAND = "hand"

    CHOICES = [
        (DRIP, "Drip"),
        (SPRINKLER, "Sprinkler"),
        (MICRO_SPRAY, "Micro spray"),
        (FLOOD, "Flood"),
        (PIVOT, "Center pivot"),
        (SUBSURFACE, "Subsurface"),
        (HAND, "Hand watering"),
    ]


class WaterSource:
    WELL = "well"
    RESERVOIR = "reservoir"
    CANAL = "canal"
    MUNICIPAL = "municipal"
    RECLAIMED = "reclaimed"
    RIVER = "river"
    RAINWATER = "rainwater"

    CHOICES = [
        (WELL, "Well"),
        (RESERVOIR, "Reservoir"),
        (CANAL, "Canal"),
        (MUNICIPAL, "Municipal"),
        (RECLAIMED, "Reclaimed"),
        (RIVER, "River"),
        (RAINWATER, "Rainwater"),
    ]


class DeviceKind:
    SOIL_MOISTURE = "soil_moisture"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    FLOW_METER = "flow_meter"
    WEATHER_STATION = "weather_station"
    PUMP = "pump"
    VALVE = "valve"
    CONTROLLER = "controller"
    RESERVOIR = "reservoir"

    CHOICES = [
        (SOIL_MOISTURE, "Soil moisture sensor"),
        (TEMPERATURE, "Temperature sensor"),
        (HUMIDITY, "Humidity sensor"),
        (FLOW_METER, "Flow meter"),
        (WEATHER_STATION, "Weather station"),
        (PUMP, "Pump"),
        (VALVE, "Valve"),
        (CONTROLLER, "Irrigation controller"),
        (RESERVOIR, "Reservoir sensor"),
    ]


class DeviceHealth:
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAULT = "fault"
    OFFLINE = "offline"

    CHOICES = [
        (HEALTHY, "Healthy"),
        (DEGRADED, "Degraded"),
        (FAULT, "Fault"),
        (OFFLINE, "Offline"),
    ]


class Connectivity:
    ONLINE = "online"
    INTERMITTENT = "intermittent"
    OFFLINE = "offline"

    CHOICES = [
        (ONLINE, "Online"),
        (INTERMITTENT, "Intermittent"),
        (OFFLINE, "Offline"),
    ]


class ScheduleKind:
    DAILY = "daily"
    WEEKLY = "weekly"
    RECURRING = "recurring"
    SEASONAL = "seasonal"

    CHOICES = [
        (DAILY, "Daily"),
        (WEEKLY, "Weekly"),
        (RECURRING, "Recurring"),
        (SEASONAL, "Seasonal"),
    ]


class RunSource:
    SCHEDULE = "schedule"
    MANUAL = "manual"
    RECOMMENDATION = "recommendation"

    CHOICES = [
        (SCHEDULE, "Schedule"),
        (MANUAL, "Manual"),
        (RECOMMENDATION, "Recommendation"),
    ]


class RunStatus:
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

    CHOICES = [
        (QUEUED, "Queued"),
        (RUNNING, "Running"),
        (PAUSED, "Paused"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
        (FAILED, "Failed"),
    ]


class RecommendationStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    EXPIRED = "expired"

    CHOICES = [
        (PENDING, "Pending approval"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (APPLIED, "Applied"),
        (EXPIRED, "Expired"),
    ]


class AlertKind:
    LOW_SOIL_MOISTURE = "low_soil_moisture"
    EXCESSIVE_WATERING = "excessive_watering"
    LEAK = "leak"
    UNUSUAL_FLOW = "unusual_flow"
    SENSOR_FAILURE = "sensor_failure"
    LOW_RESERVOIR = "low_reservoir"
    PUMP_FAULT = "pump_fault"
    DISCONNECTED_DEVICE = "disconnected_device"

    CHOICES = [
        (LOW_SOIL_MOISTURE, "Low soil moisture"),
        (EXCESSIVE_WATERING, "Excessive watering"),
        (LEAK, "Leak"),
        (UNUSUAL_FLOW, "Unusual flow"),
        (SENSOR_FAILURE, "Sensor failure"),
        (LOW_RESERVOIR, "Low reservoir"),
        (PUMP_FAULT, "Pump fault"),
        (DISCONNECTED_DEVICE, "Disconnected device"),
    ]


class AlertStatus:
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

    CHOICES = [
        (OPEN, "Open"),
        (ACKNOWLEDGED, "Acknowledged"),
        (RESOLVED, "Resolved"),
    ]


class Severity:
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    CHOICES = [
        (INFO, "Info"),
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
        (CRITICAL, "Critical"),
    ]


class AssetKind:
    PUMP = "pump"
    VALVE = "valve"
    CONTROLLER = "controller"
    FILTER = "filter"
    SENSOR = "sensor"

    CHOICES = [
        (PUMP, "Pump"),
        (VALVE, "Valve"),
        (CONTROLLER, "Controller"),
        (FILTER, "Filter"),
        (SENSOR, "Sensor"),
    ]


class MaintenanceStatus:
    SCHEDULED = "scheduled"
    DUE = "due"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    CHOICES = [
        (SCHEDULED, "Scheduled"),
        (DUE, "Due"),
        (IN_PROGRESS, "In progress"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]


class TaskStatus:
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

    CHOICES = [
        (OPEN, "Open"),
        (IN_PROGRESS, "In progress"),
        (DONE, "Done"),
        (CANCELLED, "Cancelled"),
    ]


class ReportKind:
    WATER_USAGE = "water_usage"
    ZONE_EFFICIENCY = "zone_efficiency"
    ALERT_SUMMARY = "alert_summary"
    DEVICE_HEALTH = "device_health"
    MAINTENANCE = "maintenance"
    CROP_CONSUMPTION = "crop_consumption"
    COST_ESTIMATE = "cost_estimate"

    CHOICES = [
        (WATER_USAGE, "Water usage"),
        (ZONE_EFFICIENCY, "Zone efficiency"),
        (ALERT_SUMMARY, "Alert summary"),
        (DEVICE_HEALTH, "Device health"),
        (MAINTENANCE, "Maintenance"),
        (CROP_CONSUMPTION, "Crop consumption"),
        (COST_ESTIMATE, "Cost estimate"),
    ]


class Season:
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"

    CHOICES = [
        (SPRING, "Spring"),
        (SUMMER, "Summer"),
        (AUTUMN, "Autumn"),
        (WINTER, "Winter"),
    ]
