from django.conf import settings
from django.db import models

from common.choices import ReportKind
from common.models import TenantOwnedModel


class ReportRun(TenantOwnedModel):
    kind = models.CharField(max_length=40, choices=ReportKind.CHOICES)
    status = models.CharField(max_length=20, default="ready")
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="report_runs"
    )
    result = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
