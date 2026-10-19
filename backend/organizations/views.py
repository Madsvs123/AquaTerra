from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins import PermissionMixin, TenantQuerySetMixin
from organizations.models import Membership, Organization, Team
from organizations.serializers import MembershipSerializer, OrganizationSerializer, TeamSerializer


class OrganizationViewSet(PermissionMixin, viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    required_permission = "settings.manage"
    required_read_permission = "farms.read"
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Organization.objects.filter(is_active=True)
        return Organization.objects.filter(
            memberships__user=user, memberships__is_active=True, is_active=True
        ).distinct()


class OrganizationSettingsView(PermissionMixin, APIView):
    required_permission = "settings.manage"
    required_read_permission = "farms.read"

    def get(self, request):
        org = request.organization
        return Response(
            {
                **(org.settings or {}),
                "timezone": org.timezone,
                "currency": org.currency,
                "water_unit": org.water_unit,
                "water_cost_per_unit": str(org.water_cost_per_unit),
            }
        )

    def patch(self, request):
        self.check_action_permission("settings.manage")
        org = request.organization
        current = dict(org.settings or {})
        payload = dict(request.data or {})
        for field in ("timezone", "currency", "water_unit", "water_cost_per_unit"):
            if field in payload:
                setattr(org, field, payload.pop(field))
        current.update(payload)
        org.settings = current
        org.save()
        return Response({**current, "timezone": org.timezone, "currency": org.currency, "water_unit": org.water_unit})


class TeamViewSet(TenantQuerySetMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    required_permission = "settings.manage"
    required_read_permission = "members.manage"
    search_fields = ["name"]


class MembershipViewSet(TenantQuerySetMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = Membership.objects.select_related("user", "team", "role_definition").prefetch_related(
        "assigned_farms", "assigned_zones"
    )
    serializer_class = MembershipSerializer
    required_permission = "members.manage"
    required_read_permission = "members.manage"
    search_fields = ["user__email", "user__full_name"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def perform_destroy(self, instance):
        if instance.role == "owner" and instance.user_id == self.request.user.id:
            from rest_framework.exceptions import ValidationError

            raise ValidationError("Owners cannot remove their own membership.")
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])
