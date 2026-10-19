from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response

from common.mixins import FarmScopeMixin, PermissionMixin
from farms.models import Farm, Field, IrrigationZone, Site
from farms.serializers import FarmSerializer, FieldSerializer, IrrigationZoneSerializer, SiteSerializer
from rest_framework import viewsets


class FarmViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    required_permission = "farms.write"
    required_read_permission = "farms.read"
    search_fields = ["name", "code", "address"]
    filterset_fields = ["is_active", "water_source"]
    farm_lookups = ("id",)
    zone_lookups = ()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                site_count=Count("sites", distinct=True),
                field_count=Count("fields", distinct=True),
                zone_count=Count("zones", distinct=True),
            )
        )

    @action(detail=True, methods=["get"])
    def map(self, request, pk=None):
        farm = self.get_object()
        zones = IrrigationZone.objects.filter(farm=farm).select_related("field")
        devices = farm.devices.all()
        return Response(
            {
                "farm": FarmSerializer(farm).data,
                "fields": FieldSerializer(farm.fields.all(), many=True).data,
                "zones": IrrigationZoneSerializer(zones, many=True).data,
                "devices": [
                    {
                        "id": str(device.id),
                        "name": device.name,
                        "kind": device.kind,
                        "latitude": device.latitude,
                        "longitude": device.longitude,
                        "connectivity": device.connectivity,
                    }
                    for device in devices
                ],
            }
        )


class SiteViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = Site.objects.select_related("farm")
    serializer_class = SiteSerializer
    required_permission = "farms.write"
    required_read_permission = "farms.read"
    search_fields = ["name"]
    filterset_fields = ["farm"]
    farm_lookups = ("farm",)
    zone_lookups = ()


class FieldViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = Field.objects.select_related("farm", "site")
    serializer_class = FieldSerializer
    required_permission = "farms.write"
    required_read_permission = "farms.read"
    search_fields = ["name", "crop_type"]
    filterset_fields = ["farm", "site", "crop_type", "soil_type"]
    farm_lookups = ("farm",)
    zone_lookups = ()

    def get_queryset(self):
        return super().get_queryset().annotate(zone_count=Count("zones"))


class IrrigationZoneViewSet(FarmScopeMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = IrrigationZone.objects.select_related("farm", "field")
    serializer_class = IrrigationZoneSerializer
    required_permission = "zones.write"
    required_read_permission = "zones.read"
    search_fields = ["name", "code"]
    filterset_fields = ["farm", "field", "is_active", "irrigation_method"]
    farm_lookups = ("farm",)
    zone_lookups = ("id",)
