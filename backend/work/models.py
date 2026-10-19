from django.conf import settings
from django.db import models

from common.choices import TaskStatus
from common.models import TenantOwnedModel


class WorkTask(TenantOwnedModel):
    farm = models.ForeignKey("farms.Farm", null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    zone = models.ForeignKey(
        "farms.IrrigationZone", null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks"
    )
    title = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=TaskStatus.CHOICES, default=TaskStatus.OPEN)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tasks"
    )
    due_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
