from django.conf import settings
from django.db import models

from common.choices import RunSource, RunStatus, ScheduleKind, Season
from common.models import DecimalMeasure, TenantOwnedModel


class IrrigationProgram(TenantOwnedModel):
    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="programs")
    name = models.CharField(max_length=160)
    kind = models.CharField(max_length=20, choices=ScheduleKind.CHOICES, default=ScheduleKind.WEEKLY)
    season = models.CharField(max_length=16, choices=Season.CHOICES, default=Season.SUMMER)
    seasonal_adjustment_percent = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ScheduleSlot(TenantOwnedModel):
    program = models.ForeignKey(IrrigationProgram, on_delete=models.CASCADE, related_name="slots")
    zone = models.ForeignKey("farms.IrrigationZone", on_delete=models.CASCADE, related_name="schedule_slots")
    day_of_week = models.PositiveSmallIntegerField(help_text="0=Monday")
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=20)
    flow_limit_lpm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]


class IrrigationRun(TenantOwnedModel):
    zone = models.ForeignKey("farms.IrrigationZone", on_delete=models.CASCADE, related_name="runs")
    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="runs")
    program = models.ForeignKey(
        IrrigationProgram, null=True, blank=True, on_delete=models.SET_NULL, related_name="runs"
    )
    slot = models.ForeignKey(ScheduleSlot, null=True, blank=True, on_delete=models.SET_NULL, related_name="runs")
    recommendation = models.ForeignKey(
        "recommendations.Recommendation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="runs",
    )
    source = models.CharField(max_length=24, choices=RunSource.CHOICES, default=RunSource.MANUAL)
    status = models.CharField(max_length=20, choices=RunStatus.CHOICES, default=RunStatus.QUEUED)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="irrigation_runs"
    )
    scheduled_for = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    planned_minutes = models.PositiveIntegerField(default=15)
    elapsed_seconds = models.PositiveIntegerField(default=0)
    volume_m3 = DecimalMeasure(default=0)
    peak_flow_lpm = DecimalMeasure()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"]), models.Index(fields=["zone", "status"])]


class WaterUsageRecord(TenantOwnedModel):
    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="usage_records")
    field = models.ForeignKey("farms.Field", null=True, blank=True, on_delete=models.SET_NULL, related_name="usage_records")
    zone = models.ForeignKey("farms.IrrigationZone", on_delete=models.CASCADE, related_name="usage_records")
    crop_type = models.CharField(max_length=40, blank=True)
    run = models.ForeignKey(IrrigationRun, null=True, blank=True, on_delete=models.SET_NULL, related_name="usage_records")
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    volume_m3 = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    efficiency_percent = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["-period_start"]
        indexes = [models.Index(fields=["organization", "period_start"])]
