from django.db import models

from common.choices import Connectivity, DeviceHealth, DeviceKind
from common.models import DecimalMeasure, TenantOwnedModel


class Device(TenantOwnedModel):
    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="devices")
    zone = models.ForeignKey(
        "farms.IrrigationZone", null=True, blank=True, on_delete=models.SET_NULL, related_name="devices"
    )
    name = models.CharField(max_length=160)
    serial_number = models.CharField(max_length=80)
    kind = models.CharField(max_length=40, choices=DeviceKind.CHOICES)
    manufacturer = models.CharField(max_length=80, blank=True)
    model_name = models.CharField(max_length=80, blank=True)
    firmware = models.CharField(max_length=40, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    connectivity = models.CharField(max_length=20, choices=Connectivity.CHOICES, default=Connectivity.OFFLINE)
    health = models.CharField(max_length=20, choices=DeviceHealth.CHOICES, default=DeviceHealth.HEALTHY)
    battery_percent = models.PositiveSmallIntegerField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    last_error = models.CharField(max_length=240, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "serial_number")
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "kind", "connectivity"])]

    def __str__(self):
        return self.name


class SensorReading(TenantOwnedModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="readings")
    zone = models.ForeignKey(
        "farms.IrrigationZone", null=True, blank=True, on_delete=models.SET_NULL, related_name="readings"
    )
    recorded_at = models.DateTimeField()
    soil_moisture = DecimalMeasure()
    temperature_c = DecimalMeasure()
    humidity = DecimalMeasure()
    flow_lpm = DecimalMeasure()
    rainfall_mm = DecimalMeasure()
    reservoir_percent = DecimalMeasure()
    pressure_bar = DecimalMeasure()
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [models.Index(fields=["organization", "recorded_at"]), models.Index(fields=["device", "recorded_at"])]


class DeviceHealthEvent(TenantOwnedModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="health_events")
    health = models.CharField(max_length=20, choices=DeviceHealth.CHOICES)
    connectivity = models.CharField(max_length=20, choices=Connectivity.CHOICES)
    message = models.CharField(max_length=240, blank=True)
    battery_percent = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
