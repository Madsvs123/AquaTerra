from rest_framework import serializers, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins import FarmScopeMixin, PermissionMixin
from farms.models import Farm
from weather.models import WeatherObservation
from weather.services import refresh_farm_weather


class WeatherObservationSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source="farm.name", read_only=True)

    class Meta:
        model = WeatherObservation
        fields = [
            "id",
            "farm",
            "farm_name",
            "observed_at",
            "temperature_c",
            "humidity",
            "precipitation_mm",
            "wind_kph",
            "et0_mm",
            "condition",
            "source",
        ]


class WeatherViewSet(FarmScopeMixin, PermissionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = WeatherObservation.objects.select_related("farm")
    serializer_class = WeatherObservationSerializer
    required_read_permission = "weather.read"
    filterset_fields = ["farm"]
    farm_lookups = ("farm",)
    zone_lookups = ()


class RefreshWeatherView(APIView):
    required_permission = "weather.read"

    def post(self, request):
        farm_id = request.data.get("farm")
        farms = Farm.objects.filter(organization=request.organization)
        if farm_id:
            farms = farms.filter(id=farm_id)
        created = [refresh_farm_weather(farm) for farm in farms]
        created = [item for item in created if item]
        return Response(WeatherObservationSerializer(created, many=True).data)
