from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from common.choices import SystemRole
from notifications.models import Notification
from organizations.models import Membership


def notify(*, organization, recipient, title, body="", kind="info", payload=None):
    note = Notification.objects.create(
        organization=organization,
        recipient=recipient,
        title=title,
        body=body,
        kind=kind,
        payload=payload or {},
    )
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        try:
            async_to_sync(channel_layer.group_send)(
                f"user_{recipient.id}",
                {
                    "type": "notify",
                    "payload": {
                        "id": str(note.id),
                        "title": note.title,
                        "body": note.body,
                        "kind": note.kind,
                        "payload": note.payload,
                        "created_at": note.created_at.isoformat(),
                    },
                },
            )
        except Exception:
            pass
    return note


def notify_operators(organization, title, body="", kind="info", payload=None):
    members = Membership.objects.filter(
        organization=organization,
        is_active=True,
        role__in=[SystemRole.OWNER, SystemRole.ADMIN, SystemRole.OPERATOR, SystemRole.AGRONOMIST],
    ).select_related("user")
    notes = []
    for membership in members:
        notes.append(
            notify(
                organization=organization,
                recipient=membership.user,
                title=title,
                body=body,
                kind=kind,
                payload=payload,
            )
        )
    return notes
