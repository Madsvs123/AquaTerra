from rest_framework.permissions import SAFE_METHODS, BasePermission

from common.choices import ROLE_PERMISSIONS


def membership_permissions(membership):
    if not membership or not membership.is_active:
        return set()
    if membership.role_definition_id and membership.role_definition.permissions:
        return set(membership.role_definition.permissions)
    return set(ROLE_PERMISSIONS.get(membership.role, set()))


def actor_permissions(request):
    api_key = getattr(request, "api_key", None)
    if api_key is not None:
        return set(api_key.scopes or [])
    return membership_permissions(getattr(request, "membership", None))


def has_perm(request, permission):
    if getattr(request.user, "is_superuser", False):
        return True
    perms = actor_permissions(request)
    return "*" in perms or permission in perms


class IsAuthenticatedTenant(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if getattr(view, "allow_any_authenticated", False):
            return True
        if getattr(user, "is_superuser", False):
            return True
        return getattr(request, "organization", None) is not None


class HasOrgPermission(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "is_superuser", False):
            return True
        required = getattr(view, "required_permission", None)
        if request.method in SAFE_METHODS:
            required = getattr(view, "required_read_permission", required)
        if not required:
            return True
        return has_perm(request, required)
