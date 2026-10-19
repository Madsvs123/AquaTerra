from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from accounts.authentication import ApiKeyAuthentication


class RequestContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        request.membership = None
        request.api_key = None
        user = self._authenticate(request)
        if user is not None and not isinstance(user, AnonymousUser):
            request.user = user
        if getattr(request, "user", None) and request.user.is_authenticated:
            self._bind_tenant(request)
        return self.get_response(request)

    def _authenticate(self, request):
        if request.headers.get("X-API-Key") or request.headers.get("Authorization", "").lower().startswith("apikey "):
            try:
                result = ApiKeyAuthentication().authenticate(request)
            except Exception:
                return None
            if result:
                return result[0]
            return None
        header = request.headers.get("Authorization", "")
        if not header.lower().startswith("bearer "):
            return None
        try:
            result = JWTAuthentication().authenticate(request)
        except (InvalidToken, TokenError):
            return None
        if result:
            return result[0]
        return None

    def _bind_tenant(self, request):
        from organizations.models import Membership, Organization

        if getattr(request, "api_key", None) is not None:
            org = request.api_key.organization
            request.organization = org
            request.membership = (
                Membership.objects.select_related("role_definition", "team")
                .prefetch_related("assigned_farms", "assigned_zones")
                .filter(organization=org, user=request.user, is_active=True)
                .first()
            )
            return
        header = request.headers.get("X-Organization-Id")
        qs = Organization.objects.filter(is_active=True)
        org = None
        if header:
            candidate = qs.filter(id=header).first()
            if candidate and (
                request.user.is_superuser
                or Membership.objects.filter(organization=candidate, user=request.user, is_active=True).exists()
            ):
                org = candidate
        if org is None and not header:
            membership = (
                Membership.objects.select_related("organization")
                .filter(user=request.user, is_active=True, organization__is_active=True)
                .order_by("-is_default", "created_at")
                .first()
            )
            org = membership.organization if membership else None
        request.organization = org
        if org is not None:
            request.membership = (
                Membership.objects.select_related("role_definition", "team")
                .prefetch_related("assigned_farms", "assigned_zones")
                .filter(organization=org, user=request.user, is_active=True)
                .first()
            )
