from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.mixins import TenantQuerySetMixin
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "body", "kind", "payload", "read_at", "created_at"]
        read_only_fields = fields


class NotificationViewSet(TenantQuerySetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    allow_any_authenticated = True

    def get_queryset(self):
        return Notification.objects.filter(organization=self.request.organization, recipient=self.request.user)

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        note = self.get_object()
        note.read_at = timezone.now()
        note.save(update_fields=["read_at", "updated_at"])
        return Response(NotificationSerializer(note).data)

    @action(detail=False, methods=["post"])
    def read_all(self, request):
        self.get_queryset().filter(read_at__isnull=True).update(read_at=timezone.now())
        return Response({"ok": True})
