from django.contrib import admin

from irrigation.models import IrrigationProgram, IrrigationRun, ScheduleSlot


@admin.register(IrrigationProgram)
class IrrigationProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "farm", "kind", "is_active")


@admin.register(ScheduleSlot)
class ScheduleSlotAdmin(admin.ModelAdmin):
    list_display = ("program", "zone", "day_of_week", "start_time", "duration_minutes")


@admin.register(IrrigationRun)
class IrrigationRunAdmin(admin.ModelAdmin):
    list_display = ("zone", "status", "source", "started_at", "volume_m3")
