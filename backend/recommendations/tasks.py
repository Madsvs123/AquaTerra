from celery import shared_task
from django.utils import timezone

from common.choices import RecommendationStatus
from organizations.models import Organization
from recommendations.engine import generate_for_organization
from recommendations.models import Recommendation


@shared_task
def generate_all_recommendations():
    Recommendation.objects.filter(
        status=RecommendationStatus.PENDING, expires_at__lte=timezone.now()
    ).update(status=RecommendationStatus.EXPIRED)
    for org in Organization.objects.filter(is_active=True):
        generate_for_organization(org)
