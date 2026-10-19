from rest_framework import serializers

from farms.models import Farm, Field, IrrigationZone, Site


class FarmSerializer(serializers.ModelSerializer):
    site_count = serializers.IntegerField(read_only=True)
    field_count = serializers.IntegerField(read_only=True)
    zone_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Farm
        fields = [
            "id",
            "name",
            "code",
            "description",
            "address",
            "latitude",
            "longitude",
            "area_hectares",
            "water_source",
            "timezone",
            "seasonal_config",
            "boundary",
            "is_active",
            "site_count",
            "field_count",
            "zone_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SiteSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source="farm.name", read_only=True)

    class Meta:
        model = Site
        fields = [
            "id",
            "farm",
            "farm_name",
            "name",
            "kind",
            "latitude",
            "longitude",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class FieldSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source="farm.name", read_only=True)
    site_name = serializers.CharField(source="site.name", read_only=True)
    zone_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Field
        fields = [
            "id",
            "farm",
            "farm_name",
            "site",
            "site_name",
            "name",
            "crop_type",
            "soil_type",
            "irrigation_method",
            "planting_date",
            "harvest_date",
            "area_hectares",
            "boundary",
            "notes",
            "zone_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class IrrigationZoneSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source="farm.name", read_only=True)
    field_name = serializers.CharField(source="field.name", read_only=True)
    crop_type = serializers.CharField(source="field.crop_type", read_only=True)
    soil_type = serializers.CharField(source="field.soil_type", read_only=True)

    class Meta:
        model = IrrigationZone
        fields = [
            "id",
            "farm",
            "farm_name",
            "field",
            "field_name",
            "crop_type",
            "soil_type",
            "name",
            "code",
            "irrigation_method",
            "water_source",
            "target_moisture_min",
            "target_moisture_max",
            "flow_limit_lpm",
            "area_hectares",
            "season",
            "seasonal_config",
            "boundary",
            "require_recommendation_approval",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
