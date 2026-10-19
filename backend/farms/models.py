from django.db import models

from common.choices import CropType, IrrigationMethod, Season, SoilType, WaterSource
from common.models import DecimalMeasure, TenantOwnedModel


class Farm(TenantOwnedModel):
    name = models.CharField(max_length=160)
    code = models.SlugField(max_length=40)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=240, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    area_hectares = DecimalMeasure(default=0)
    water_source = models.CharField(max_length=32, choices=WaterSource.CHOICES, default=WaterSource.WELL)
    timezone = models.CharField(max_length=64, blank=True)
    seasonal_config = models.JSONField(default=dict, blank=True)
    boundary = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organization", "code")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Site(TenantOwnedModel):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="sites")
    name = models.CharField(max_length=160)
    kind = models.CharField(max_length=40, default="block")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("farm", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Field(TenantOwnedModel):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="fields")
    site = models.ForeignKey(Site, null=True, blank=True, on_delete=models.SET_NULL, related_name="fields")
    name = models.CharField(max_length=160)
    crop_type = models.CharField(max_length=40, choices=CropType.CHOICES, default=CropType.MIXED)
    soil_type = models.CharField(max_length=40, choices=SoilType.CHOICES, default=SoilType.LOAM)
    irrigation_method = models.CharField(max_length=40, choices=IrrigationMethod.CHOICES, default=IrrigationMethod.DRIP)
    planting_date = models.DateField(null=True, blank=True)
    harvest_date = models.DateField(null=True, blank=True)
    area_hectares = DecimalMeasure(default=0)
    boundary = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("farm", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class IrrigationZone(TenantOwnedModel):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="zones")
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="zones")
    name = models.CharField(max_length=160)
    code = models.SlugField(max_length=40)
    irrigation_method = models.CharField(max_length=40, choices=IrrigationMethod.CHOICES, default=IrrigationMethod.DRIP)
    water_source = models.CharField(max_length=32, choices=WaterSource.CHOICES, default=WaterSource.WELL)
    target_moisture_min = models.DecimalField(max_digits=5, decimal_places=2, default=22)
    target_moisture_max = models.DecimalField(max_digits=5, decimal_places=2, default=38)
    flow_limit_lpm = models.DecimalField(max_digits=8, decimal_places=2, default=40)
    area_hectares = DecimalMeasure(default=0)
    season = models.CharField(max_length=16, choices=Season.CHOICES, default=Season.SUMMER)
    seasonal_config = models.JSONField(default=dict, blank=True)
    boundary = models.JSONField(default=list, blank=True)
    require_recommendation_approval = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("farm", "code")
        ordering = ["name"]

    def __str__(self):
        return self.name
