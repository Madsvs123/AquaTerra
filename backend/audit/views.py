from rest_framework import serializers, viewsets

from audit.models import AuditLog
from common.mixins import PermissionMixin, TenantQuerySetMixin


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "actor_email", "action", "path", "resource_type", "status_code", "created_at"]


class AuditLogViewSet(TenantQuerySetMixin, PermissionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    required_read_permission = "audit.read"
    filterset_fields = ["action", "resource_type"]
    search_fields = ["path", "actor_email"]
