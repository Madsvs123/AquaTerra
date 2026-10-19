from rest_framework.response import Response
from rest_framework.views import APIView

from alerts.models import Alert
from devices.models import Device
from farms.models import Farm, IrrigationZone
from irrigation.models import IrrigationProgram
from maintenance.models import WorkOrder


class SearchView(APIView):
    required_read_permission = "farms.read"

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        org = request.organization
        if not q:
            return Response({"farms": [], "zones": [], "devices": [], "alerts": [], "programs": [], "work_orders": []})
        return Response(
            {
                "farms": [
                    {"id": str(item.id), "label": item.name, "meta": item.code}
                    for item in Farm.objects.filter(organization=org, name__icontains=q)[:8]
                ],
                "zones": [
                    {"id": str(item.id), "label": item.name, "meta": item.farm.name}
                    for item in IrrigationZone.objects.select_related("farm").filter(organization=org, name__icontains=q)[:8]
                ],
                "devices": [
                    {"id": str(item.id), "label": item.name, "meta": item.kind}
                    for item in Device.objects.filter(organization=org, name__icontains=q)[:8]
                ],
                "alerts": [
                    {"id": str(item.id), "label": item.title, "meta": item.severity}
                    for item in Alert.objects.filter(organization=org, title__icontains=q)[:8]
                ],
                "programs": [
                    {"id": str(item.id), "label": item.name, "meta": item.kind}
                    for item in IrrigationProgram.objects.filter(organization=org, name__icontains=q)[:8]
                ],
                "work_orders": [
                    {"id": str(item.id), "label": item.title, "meta": item.status}
                    for item in WorkOrder.objects.filter(organization=org, title__icontains=q)[:8]
                ],
            }
        )
