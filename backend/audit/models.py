from django.conf import settings
from django.db import models

from common.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization", null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs"
    )
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    actor_email = models.EmailField(blank=True)
    action = models.CharField(max_length=16)
    path = models.CharField(max_length=240)
    resource_type = models.CharField(max_length=80, blank=True)
    status_code = models.PositiveSmallIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
