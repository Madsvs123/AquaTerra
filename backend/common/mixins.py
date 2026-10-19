from django.db.models import Q
from rest_framework.exceptions import PermissionDenied

from common.choices import SystemRole
from common.permissions import has_perm


class TenantQuerySetMixin:
    organization_field = "organization"

    def get_queryset(self):
        qs = super().get_queryset()
        org = getattr(self.request, "organization", None)
        if org is None:
            return qs.none()
        return qs.filter(**{self.organization_field: org})

    def perform_create(self, serializer):
        org = getattr(self.request, "organization", None)
        if org is None:
            raise PermissionDenied("Organization context is required.")
        extra = {}
        model = serializer.Meta.model
        field_names = {field.name for field in model._meta.fields}
        if "created_by" in field_names and "created_by" not in serializer.validated_data:
            extra["created_by"] = self.request.user
        serializer.save(organization=org, **extra)


class FarmScopeMixin(TenantQuerySetMixin):
    """Restricts records to farms and zones granted on the membership."""

    farm_lookups = ("farm",)
    zone_lookups = ("zone",)

    def get_queryset(self):
        qs = super().get_queryset()
        membership = getattr(self.request, "membership", None)
        if not membership or membership.role in {SystemRole.OWNER, SystemRole.ADMIN}:
            return qs
        if not membership.restrict_to_assigned:
            return qs

        farm_ids = list(membership.assigned_farms.values_list("id", flat=True))
        zone_ids = list(membership.assigned_zones.values_list("id", flat=True))
        field_names = {field.name for field in qs.model._meta.fields}
        related = {rel.name for rel in qs.model._meta.related_objects}
        q = Q()
        matched = False
        for lookup in self.farm_lookups:
            if lookup in field_names or lookup in related or "__" in lookup:
                q |= Q(**{f"{lookup}__in": farm_ids})
                matched = True
        for lookup in self.zone_lookups:
            if lookup in field_names or lookup in related or "__" in lookup:
                q |= Q(**{f"{lookup}__in": zone_ids})
                matched = True
        if not matched:
            return qs
        if not farm_ids and not zone_ids:
            return qs.none()
        return qs.filter(q).distinct()


class PermissionMixin:
    required_permission = None
    required_read_permission = None

    def check_action_permission(self, permission):
        if not has_perm(self.request, permission):
            raise PermissionDenied("You do not have permission to perform this action.")
