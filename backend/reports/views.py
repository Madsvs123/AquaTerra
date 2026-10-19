import csv

from django.http import HttpResponse
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from common.choices import ReportKind
from common.mixins import PermissionMixin, TenantQuerySetMixin
from reports.models import ReportRun
from reports.services import build_report


class ReportRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportRun
        fields = ["id", "kind", "status", "result", "created_at"]
        read_only_fields = ["id", "status", "result", "created_at"]


class ReportCatalogView(APIView):
    required_read_permission = "reports.read"

    def get(self, request):
        return Response({"kinds": [{"key": key, "label": label} for key, label in ReportKind.CHOICES]})


class ReportRunViewSet(TenantQuerySetMixin, PermissionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ReportRun.objects.all()
    serializer_class = ReportRunSerializer
    required_read_permission = "reports.read"

    def create(self, request, *args, **kwargs):
        kind = request.data.get("kind") or ReportKind.WATER_USAGE
        result = build_report(request.organization, kind)
        run = ReportRun.objects.create(
            organization=request.organization,
            kind=kind,
            status="ready",
            requested_by=request.user,
            result=result,
        )
        return Response(ReportRunSerializer(run).data, status=201)

    @action(detail=True, methods=["get"])
    def export(self, request, pk=None):
        self.check_action_permission("reports.export")
        run = self.get_object()
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{run.kind}.csv"'
        writer = csv.writer(response)
        rows = run.result.get("rows") or []
        if rows:
            if isinstance(rows[0], dict):
                writer.writerow(list(rows[0].keys()))
                for row in rows:
                    writer.writerow(list(row.values()))
            else:
                writer.writerow(["value"])
                for row in rows:
                    writer.writerow([row])
        return response


class ReportExportView(APIView):
    required_permission = "reports.export"
    required_read_permission = "reports.export"

    def get(self, request):
        kind = request.query_params.get("kind") or ReportKind.WATER_USAGE
        result = build_report(request.organization, kind)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{kind}.csv"'
        writer = csv.writer(response)
        rows = result.get("rows") or []
        if rows and isinstance(rows[0], dict):
            writer.writerow(list(rows[0].keys()))
            for row in rows:
                writer.writerow(list(row.values()))
        return response
