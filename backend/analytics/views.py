from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.models import UsageSnapshot
from analytics.services import dashboard, water_analytics


class DashboardView(APIView):
    required_read_permission = "analytics.read"

    def get(self, request):
        return Response(dashboard(request.organization))


class WaterAnalyticsView(APIView):
    required_read_permission = "analytics.read"

    def get(self, request):
        return Response(water_analytics(request.organization, days=request.query_params.get("days", 14)))


class SnapshotView(APIView):
    required_read_permission = "analytics.read"

    def get(self, request):
        rows = UsageSnapshot.objects.filter(organization=request.organization)[:30]
        return Response([{"id": str(row.id), "captured_on": row.captured_on, "payload": row.payload} for row in rows])
