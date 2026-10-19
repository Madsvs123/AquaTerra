from django.conf import settings
from django.db import models

from common.choices import RecommendationStatus
from common.models import TenantOwnedModel


class Recommendation(TenantOwnedModel):
    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="recommendations")
    zone = models.ForeignKey("farms.IrrigationZone", on_delete=models.CASCADE, related_name="recommendations")
    title = models.CharField(max_length=200)
    rationale = models.TextField()
    suggested_minutes = models.PositiveIntegerField(default=15)
    suggested_volume_m3 = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=70)
    factors = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=RecommendationStatus.CHOICES, default=RecommendationStatus.PENDING)
    requires_approval = models.BooleanField(default=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="recommendation_decisions"
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status"])]
