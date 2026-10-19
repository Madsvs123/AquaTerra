from celery import shared_task
from django.utils import timezone

from common.choices import MaintenanceStatus
from maintenance.models import ServiceSchedule, WorkOrder
from notifications.services import notify_operators


@shared_task
def flag_due_maintenance():
    today = timezone.now().date()
    for schedule in ServiceSchedule.objects.select_related("asset", "organization").filter(
        is_active=True, next_due_on__lte=today
    ):
        existing = WorkOrder.objects.filter(
            organization=schedule.organization,
            asset=schedule.asset,
            title=schedule.title,
            status__in=[MaintenanceStatus.SCHEDULED, MaintenanceStatus.DUE, MaintenanceStatus.IN_PROGRESS],
        ).exists()
        if existing:
            continue
        WorkOrder.objects.create(
            organization=schedule.organization,
            asset=schedule.asset,
            farm=schedule.asset.farm,
            title=schedule.title,
            details=f"Due service for {schedule.asset.name}",
            status=MaintenanceStatus.DUE,
            assigned_to=schedule.assigned_to,
            due_on=schedule.next_due_on,
        )
        notify_operators(
            schedule.organization,
            title=f"Maintenance due: {schedule.asset.name}",
            body=schedule.title,
            kind="maintenance",
        )
