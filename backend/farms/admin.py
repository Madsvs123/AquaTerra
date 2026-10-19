from django.contrib import admin

from farms.models import Farm, Field, IrrigationZone, Site


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "organization", "water_source")


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "farm")


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("name", "farm", "crop_type", "soil_type")


@admin.register(IrrigationZone)
class IrrigationZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "farm", "is_active")
