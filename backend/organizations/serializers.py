from rest_framework import serializers

from accounts.models import User
from organizations.models import Membership, Organization, Team


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "industry",
            "timezone",
            "currency",
            "water_unit",
            "water_cost_per_unit",
            "plan",
            "is_active",
            "settings",
            "created_at",
        ]
        read_only_fields = ["id", "slug", "is_active", "created_at"]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(write_only=True, required=False)
    assigned_farm_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="assigned_farms"
    )
    assigned_zone_ids = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="assigned_zones"
    )

    class Meta:
        model = Membership
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "email",
            "role",
            "role_definition",
            "team",
            "assigned_farms",
            "assigned_zones",
            "assigned_farm_ids",
            "assigned_zone_ids",
            "is_default",
            "is_active",
            "restrict_to_assigned",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]

    def validate(self, attrs):
        email = attrs.pop("email", None)
        if self.instance is None and email:
            user = User.objects.filter(email=email.lower()).first()
            if not user:
                raise serializers.ValidationError({"email": "No account exists for that email. Send an invitation."})
            attrs["user"] = user
        if self.instance is None and "user" not in attrs:
            raise serializers.ValidationError({"email": "Provide an email for an existing account."})
        return attrs
