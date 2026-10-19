from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from common.choices import RunSource
from irrigation.models import ScheduleSlot
from irrigation.services import complete_elapsed_runs, start_run
from organizations.models import Organization


@shared_task
def run_due_schedules():
    now = timezone.now()
    weekday = now.weekday()
    window_start = (now - timedelta(minutes=1)).time()
    window_end = (now + timedelta(minutes=1)).time()
    for org in Organization.objects.filter(is_active=True):
        slots = ScheduleSlot.objects.select_related("program", "zone").filter(
            organization=org,
            is_active=True,
            program__is_active=True,
            day_of_week=weekday,
            start_time__gte=window_start,
            start_time__lte=window_end,
        )
        for slot in slots:
            minutes = slot.duration_minutes
            if slot.program.seasonal_adjustment_percent:
                minutes = max(1, int(minutes * (100 + slot.program.seasonal_adjustment_percent) / 100))
            start_run(
                organization=org,
                zone=slot.zone,
                source=RunSource.SCHEDULE,
                minutes=minutes,
                program=slot.program,
                slot=slot,
                notes="Scheduled watering",
            )
    complete_elapsed_runs()
