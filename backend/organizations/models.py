from django.conf import settings
from django.db import models
from django.utils.text import slugify

from common.choices import SystemRole
from common.models import TenantOwnedModel, TimeStampedModel


class Organization(TimeStampedModel):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=80, unique=True)
    industry = models.CharField(max_length=80, blank=True, default="agriculture")
    timezone = models.CharField(max_length=64, default="UTC")
    currency = models.CharField(max_length=8, default="USD")
    water_unit = models.CharField(max_length=16, default="m3")
    water_cost_per_unit = models.DecimalField(max_digits=10, decimal_places=4, default=0.45)
    plan = models.CharField(max_length=40, default="operations")
    is_active = models.BooleanField(default=True)
    settings = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class Team(TenantOwnedModel):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("organization", "name")

    def __str__(self):
        return self.name


class Membership(TenantOwnedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=40, choices=SystemRole.CHOICES, default=SystemRole.VIEWER)
    role_definition = models.ForeignKey(
        "accounts.RoleDefinition", null=True, blank=True, on_delete=models.SET_NULL, related_name="memberships"
    )
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="memberships")
    assigned_farms = models.ManyToManyField("farms.Farm", blank=True, related_name="member_access")
    assigned_zones = models.ManyToManyField("farms.IrrigationZone", blank=True, related_name="member_access")
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    restrict_to_assigned = models.BooleanField(default=False)

    class Meta:
        unique_together = ("organization", "user")

    def __str__(self):
        return f"{self.user} @ {self.organization}"


def default_org_settings():
    return {
        "require_recommendation_approval": True,
        "low_moisture_buffer": 2,
        "excessive_watering_percent": 125,
        "leak_flow_multiplier": 1.8,
        "reservoir_low_percent": 20,
        "device_offline_minutes": 5,
        "notify_operators": True,
        "data_retention_days": 730,
        "default_season": "summer",
        "currency": "USD",
        "water_unit": "m3",
    }


def slugify_unique(name):
    base = slugify(name)[:70] or "org"
    slug = base
    index = 2
    while Organization.objects.filter(slug=slug).exists():
        slug = f"{base}-{index}"
        index += 1
    return slug
