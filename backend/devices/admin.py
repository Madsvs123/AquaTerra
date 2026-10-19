from django.contrib import admin

from devices.models import Device, SensorReading


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "farm", "connectivity", "health", "last_seen_at")


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ("device", "recorded_at", "soil_moisture", "flow_lpm")
