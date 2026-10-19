from celery import shared_task
from django.utils import timezone

from analytics.models import UsageSnapshot
from analytics.services import water_analytics
from organizations.models import Organization


@shared_task
def capture_usage_snapshots():
    today = timezone.now().date()
    for org in Organization.objects.filter(is_active=True):
        UsageSnapshot.objects.update_or_create(
            organization=org,
            captured_on=today,
            defaults={"payload": water_analytics(org, days=1)},
        )
