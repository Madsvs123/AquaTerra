from django.conf import settings
from django.db import models

from common.choices import AssetKind, MaintenanceStatus
from common.models import TenantOwnedModel


class Asset(TenantOwnedModel):
    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="assets")
    zone = models.ForeignKey(
        "farms.IrrigationZone", null=True, blank=True, on_delete=models.SET_NULL, related_name="assets"
    )
    device = models.ForeignKey(
        "devices.Device", null=True, blank=True, on_delete=models.SET_NULL, related_name="assets"
    )
    name = models.CharField(max_length=160)
    kind = models.CharField(max_length=32, choices=AssetKind.CHOICES)
    installed_on = models.DateField(null=True, blank=True)
    serial_number = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]


class ServiceSchedule(TenantOwnedModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="schedules")
    title = models.CharField(max_length=160)
    interval_days = models.PositiveIntegerField(default=90)
    next_due_on = models.DateField()
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="service_schedules"
    )
    is_active = models.BooleanField(default=True)


class Inspection(TenantOwnedModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="inspections")
    inspected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="inspections"
    )
    inspected_on = models.DateField()
    result = models.CharField(max_length=40, default="pass")
    notes = models.TextField(blank=True)


class WorkOrder(TenantOwnedModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="work_orders")
    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="work_orders")
    title = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=MaintenanceStatus.CHOICES, default=MaintenanceStatus.SCHEDULED)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="work_orders"
    )
    due_on = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
