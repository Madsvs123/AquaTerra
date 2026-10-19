from common.choices import ROLE_PERMISSIONS, SystemRole
from organizations.models import Team, default_org_settings


def bootstrap_organization(organization):
    from accounts.models import RoleDefinition
    from alerts.models import AlertRule
    from common.choices import AlertKind, Severity

    if not organization.settings:
        organization.settings = default_org_settings()
        organization.save(update_fields=["settings", "updated_at"])

    Team.objects.get_or_create(
        organization=organization,
        name="Field operations",
        defaults={"description": "Primary irrigation and field crew"},
    )

    for role, perms in ROLE_PERMISSIONS.items():
        if role == SystemRole.OWNER:
            continue
        RoleDefinition.objects.get_or_create(
            organization=organization,
            slug=role,
            defaults={
                "name": role.replace("_", " ").title(),
                "base_role": role,
                "permissions": sorted(perms),
                "description": f"Default {role.replace('_', ' ')} access",
            },
        )

    defaults = [
        (AlertKind.LOW_SOIL_MOISTURE, "Low soil moisture", {"below_target": True}, Severity.HIGH),
        (AlertKind.EXCESSIVE_WATERING, "Excessive watering", {"percent": 125}, Severity.MEDIUM),
        (AlertKind.LEAK, "Possible leak", {"flow_multiplier": 1.8}, Severity.CRITICAL),
        (AlertKind.UNUSUAL_FLOW, "Unusual flow", {"deviation_percent": 40}, Severity.HIGH),
        (AlertKind.SENSOR_FAILURE, "Sensor failure", {"stale_minutes": 30}, Severity.HIGH),
        (AlertKind.LOW_RESERVOIR, "Low reservoir", {"percent": 20}, Severity.HIGH),
        (AlertKind.PUMP_FAULT, "Pump fault", {}, Severity.CRITICAL),
        (AlertKind.DISCONNECTED_DEVICE, "Disconnected device", {"offline_minutes": 5}, Severity.MEDIUM),
    ]
    for kind, name, threshold, severity in defaults:
        AlertRule.objects.get_or_create(
            organization=organization,
            kind=kind,
            name=name,
            defaults={"threshold": threshold, "severity": severity, "is_active": True},
        )
