from django.conf import settings
from django.db import models

from common.choices import AlertKind, AlertStatus, Severity
from common.models import TenantOwnedModel


class AlertRule(TenantOwnedModel):
    farm = models.ForeignKey("farms.Farm", null=True, blank=True, on_delete=models.CASCADE, related_name="alert_rules")
    zone = models.ForeignKey(
        "farms.IrrigationZone", null=True, blank=True, on_delete=models.CASCADE, related_name="alert_rules"
    )
    name = models.CharField(max_length=160)
    kind = models.CharField(max_length=40, choices=AlertKind.CHOICES)
    severity = models.CharField(max_length=20, choices=Severity.CHOICES, default=Severity.MEDIUM)
    threshold = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]


class Alert(TenantOwnedModel):
    rule = models.ForeignKey(AlertRule, null=True, blank=True, on_delete=models.SET_NULL, related_name="alerts")
    farm = models.ForeignKey("farms.Farm", null=True, blank=True, on_delete=models.CASCADE, related_name="alerts")
    zone = models.ForeignKey(
        "farms.IrrigationZone", null=True, blank=True, on_delete=models.SET_NULL, related_name="alerts"
    )
    device = models.ForeignKey(
        "devices.Device", null=True, blank=True, on_delete=models.SET_NULL, related_name="alerts"
    )
    kind = models.CharField(max_length=40, choices=AlertKind.CHOICES)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=Severity.CHOICES, default=Severity.MEDIUM)
    status = models.CharField(max_length=20, choices=AlertStatus.CHOICES, default=AlertStatus.OPEN)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="acknowledged_alerts"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "kind"])]
