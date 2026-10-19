from celery import shared_task

from farms.models import Farm
from weather.services import refresh_farm_weather


@shared_task
def refresh_all_weather():
    for farm in Farm.objects.filter(is_active=True, latitude__isnull=False, longitude__isnull=False):
        refresh_farm_weather(farm)
