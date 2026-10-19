from rest_framework import serializers

from recommendations.models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    farm_name = serializers.CharField(source="farm.name", read_only=True)
    decided_by_name = serializers.CharField(source="decided_by.full_name", read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            "id",
            "farm",
            "farm_name",
            "zone",
            "zone_name",
            "title",
            "rationale",
            "suggested_minutes",
            "suggested_volume_m3",
            "confidence",
            "factors",
            "status",
            "requires_approval",
            "decided_by",
            "decided_by_name",
            "decided_at",
            "expires_at",
            "created_at",
        ]
        read_only_fields = ["id", "status", "decided_by", "decided_at", "created_at"]
