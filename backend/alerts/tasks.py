from celery import shared_task

from alerts.engine import evaluate_organization
from organizations.models import Organization


@shared_task
def evaluate_all_organizations():
    for org in Organization.objects.filter(is_active=True):
        evaluate_organization(org)
