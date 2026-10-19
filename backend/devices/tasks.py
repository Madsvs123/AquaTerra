from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from common.choices import Connectivity, DeviceHealth
from devices.models import Device, DeviceHealthEvent
from organizations.models import Organization


@shared_task
def check_device_health():
    cutoff = timezone.now() - timedelta(seconds=settings.DEVICE_OFFLINE_SECONDS)
    for org in Organization.objects.filter(is_active=True):
        stale = Device.objects.filter(organization=org, is_active=True).exclude(last_seen_at__gte=cutoff)
        for device in stale:
            if device.connectivity == Connectivity.OFFLINE and device.health == DeviceHealth.OFFLINE:
                continue
            device.connectivity = Connectivity.OFFLINE
            device.health = DeviceHealth.OFFLINE
            device.last_error = "No telemetry within the configured window"
            device.save(update_fields=["connectivity", "health", "last_error", "updated_at"])
            DeviceHealthEvent.objects.create(
                organization=org,
                device=device,
                health=device.health,
                connectivity=device.connectivity,
                message=device.last_error,
                battery_percent=device.battery_percent,
            )
