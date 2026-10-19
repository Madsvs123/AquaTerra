from celery import shared_task
from django.utils import timezone

from accounts.models import Invitation
from common.choices import InvitationStatus


@shared_task
def expire_invitations():
    Invitation.objects.filter(status=InvitationStatus.PENDING, expires_at__lte=timezone.now()).update(
        status=InvitationStatus.EXPIRED
    )
