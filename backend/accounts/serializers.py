from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import ApiKey, Invitation, RoleDefinition, User
from organizations.models import Membership


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "title", "phone", "is_active", "date_joined"]
        read_only_fields = ["id", "is_active", "date_joined"]


class MembershipBriefSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    organization_slug = serializers.CharField(source="organization.slug", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "organization",
            "organization_name",
            "organization_slug",
            "role",
            "team",
            "team_name",
            "is_default",
            "is_active",
            "restrict_to_assigned",
        ]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(max_length=160)
    organization_name = serializers.CharField(max_length=160)
    title = serializers.CharField(max_length=120, required=False, allow_blank=True)

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def validate_password(self, value):
        validate_password(value)
        return value


class LoginSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = [
            "id",
            "email",
            "role",
            "role_definition",
            "team",
            "assigned_farms",
            "assigned_zones",
            "restrict_to_assigned",
            "status",
            "expires_at",
            "accepted_at",
            "created_at",
        ]
        read_only_fields = ["id", "status", "expires_at", "accepted_at", "created_at"]


class AcceptInviteSerializer(serializers.Serializer):
    token = serializers.CharField()
    full_name = serializers.CharField(max_length=160)
    password = serializers.CharField(write_only=True)
    title = serializers.CharField(max_length=120, required=False, allow_blank=True)

    def validate_password(self, value):
        validate_password(value)
        return value


class RoleDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleDefinition
        fields = ["id", "name", "slug", "base_role", "permissions", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = [
            "id",
            "name",
            "prefix",
            "scopes",
            "last_used_at",
            "expires_at",
            "revoked_at",
            "created_at",
        ]
        read_only_fields = ["id", "prefix", "last_used_at", "revoked_at", "created_at"]


class ApiKeyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    scopes = serializers.ListField(child=serializers.CharField(), allow_empty=False)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
