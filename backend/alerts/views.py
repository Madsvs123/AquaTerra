from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from alerts.engine import evaluate_organization
from alerts.models import Alert, AlertRule
from alerts.serializers import AlertRuleSerializer, AlertSerializer
from common.choices import AlertStatus
from common.mixins import FarmScopeMixin, PermissionMixin


class AlertRuleViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    required_permission = "alerts.write"
    required_read_permission = "alerts.read"
    filterset_fields = ["kind", "is_active", "farm", "zone"]
    farm_lookups = ("farm",)
    zone_lookups = ("zone",)


class AlertViewSet(FarmScopeMixin, PermissionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Alert.objects.select_related("farm", "zone", "device", "rule")
    serializer_class = AlertSerializer
    required_read_permission = "alerts.read"
    filterset_fields = ["kind", "status", "severity", "farm", "zone"]
    search_fields = ["title", "body"]
    farm_lookups = ("farm",)
    zone_lookups = ("zone",)

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        self.check_action_permission("alerts.write")
        alert = self.get_object()
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = request.user
        alert.save(update_fields=["status", "acknowledged_by", "updated_at"])
        return Response(AlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        self.check_action_permission("alerts.write")
        alert = self.get_object()
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = timezone.now()
        alert.save(update_fields=["status", "resolved_at", "updated_at"])
        return Response(AlertSerializer(alert).data)


class EvaluateAlertsView(APIView):
    required_permission = "alerts.write"

    def post(self, request):
        created = evaluate_organization(request.organization)
        return Response({"created": AlertSerializer(created, many=True).data, "count": len(created)})
