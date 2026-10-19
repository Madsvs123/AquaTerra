from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from common.choices import RecommendationStatus, RunSource
from common.mixins import FarmScopeMixin, PermissionMixin
from irrigation.serializers import IrrigationRunSerializer
from irrigation.services import start_run
from recommendations.engine import generate_for_organization
from recommendations.models import Recommendation
from recommendations.serializers import RecommendationSerializer


class RecommendationViewSet(FarmScopeMixin, PermissionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Recommendation.objects.select_related("farm", "zone", "decided_by")
    serializer_class = RecommendationSerializer
    required_read_permission = "recommendations.read"
    filterset_fields = ["farm", "zone", "status"]
    farm_lookups = ("farm",)
    zone_lookups = ("zone",)

    def _decide(self, recommendation, status):
        if recommendation.status != RecommendationStatus.PENDING:
            raise ValidationError("Recommendation is no longer pending.")
        recommendation.status = status
        recommendation.decided_by = self.request.user
        recommendation.decided_at = timezone.now()
        recommendation.save(update_fields=["status", "decided_by", "decided_at", "updated_at"])
        return recommendation

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        self.check_action_permission("recommendations.approve")
        rec = self._decide(self.get_object(), RecommendationStatus.APPROVED)
        run = start_run(
            organization=request.organization,
            zone=rec.zone,
            user=request.user,
            source=RunSource.RECOMMENDATION,
            minutes=rec.suggested_minutes,
            recommendation=rec,
            notes=rec.title,
        )
        rec.status = RecommendationStatus.APPLIED
        rec.save(update_fields=["status", "updated_at"])
        return Response({"recommendation": RecommendationSerializer(rec).data, "run": IrrigationRunSerializer(run).data})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        self.check_action_permission("recommendations.approve")
        rec = self._decide(self.get_object(), RecommendationStatus.REJECTED)
        return Response(RecommendationSerializer(rec).data)


class GenerateRecommendationsView(APIView):
    required_permission = "recommendations.approve"
    required_read_permission = "recommendations.read"

    def post(self, request):
        created = generate_for_organization(request.organization)
        return Response({"created": RecommendationSerializer(created, many=True).data, "count": len(created)})
