from django.db import models

from common.models import TenantOwnedModel


class UsageSnapshot(TenantOwnedModel):
    captured_on = models.DateField()
    payload = models.JSONField(default=dict)

    class Meta:
        unique_together = ("organization", "captured_on")
        ordering = ["-captured_on"]
