from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.authentication import generate_api_key
from accounts.models import ApiKey, Invitation, RoleDefinition, User
from accounts.serializers import (
    AcceptInviteSerializer,
    ApiKeyCreateSerializer,
    ApiKeySerializer,
    InvitationSerializer,
    LoginSerializer,
    MembershipBriefSerializer,
    RegisterSerializer,
    RoleDefinitionSerializer,
    UserSerializer,
)
from common.choices import ALL_PERMISSIONS, InvitationStatus, SystemRole
from common.mixins import PermissionMixin, TenantQuerySetMixin
from organizations.models import Membership
from organizations.services import bootstrap_organization, slugify_unique


def issue_tokens(user):
    refresh = RefreshToken.for_user(user)
    memberships = Membership.objects.select_related("organization", "team").filter(user=user, is_active=True)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserSerializer(user).data,
        "memberships": MembershipBriefSerializer(memberships, many=True).data,
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = User.objects.create_user(
            username=data["email"],
            email=data["email"],
            password=data["password"],
            full_name=data["full_name"],
            title=data.get("title", ""),
            first_name=data["full_name"].split(" ")[0],
        )
        from organizations.models import Organization

        org = Organization.objects.create(
            name=data["organization_name"],
            slug=slugify_unique(data["organization_name"]),
        )
        bootstrap_organization(org)
        Membership.objects.create(
            organization=org,
            user=user,
            role=SystemRole.OWNER,
            is_default=True,
            is_active=True,
        )
        return Response(issue_tokens(user), status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        email = (request.data.get("email") or request.data.get("username") or "").strip().lower()
        user = User.objects.filter(email=email).first()
        if user:
            payload = issue_tokens(user)
            response.data["user"] = payload["user"]
            response.data["memberships"] = payload["memberships"]
            response.data["refresh"] = payload["refresh"]
            response.data["access"] = payload["access"]
        return response


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    authentication_classes = []


class LogoutView(APIView):
    allow_any_authenticated = True

    def post(self, request):
        token = request.data.get("refresh")
        if token:
            try:
                RefreshToken(token).blacklist()
            except Exception:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    allow_any_authenticated = True

    def get(self, request):
        memberships = Membership.objects.select_related("organization", "team").filter(user=request.user, is_active=True)
        from common.permissions import actor_permissions

        return Response(
            {
                "user": UserSerializer(request.user).data,
                "memberships": MembershipBriefSerializer(memberships, many=True).data,
                "permissions": sorted(actor_permissions(request)),
            }
        )

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class InvitationViewSet(TenantQuerySetMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    required_permission = "members.manage"
    required_read_permission = "members.manage"
    http_method_names = ["get", "post", "delete", "head", "options"]

    def perform_create(self, serializer):
        self.check_action_permission("members.manage")
        import secrets

        invitation = serializer.save(
            organization=self.request.organization,
            invited_by=self.request.user,
            token=secrets.token_urlsafe(32),
            status=InvitationStatus.PENDING,
            expires_at=timezone.now() + timedelta(days=14),
        )
        link = f"{settings.FRONTEND_URL}/invite/{invitation.token}"
        send_mail(
            subject=f"Join {self.request.organization.name} on AquaTerra",
            message=(
                f"You have been invited to {self.request.organization.name} as {invitation.role}.\n\n"
                f"Accept the invitation: {link}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.email],
            fail_silently=True,
        )

    def perform_destroy(self, instance):
        instance.status = InvitationStatus.REVOKED
        instance.save(update_fields=["status", "updated_at"])


class AcceptInviteView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @transaction.atomic
    def post(self, request):
        serializer = AcceptInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        invitation = Invitation.objects.select_related("organization").filter(token=data["token"]).first()
        if not invitation or invitation.status != InvitationStatus.PENDING:
            return Response({"detail": "Invitation is no longer valid."}, status=status.HTTP_400_BAD_REQUEST)
        if invitation.expires_at <= timezone.now():
            invitation.status = InvitationStatus.EXPIRED
            invitation.save(update_fields=["status", "updated_at"])
            return Response({"detail": "Invitation has expired."}, status=status.HTTP_400_BAD_REQUEST)
        user, created = User.objects.get_or_create(
            email=invitation.email.lower(),
            defaults={
                "username": invitation.email.lower(),
                "full_name": data["full_name"],
                "title": data.get("title", ""),
            },
        )
        if created:
            user.set_password(data["password"])
            user.full_name = data["full_name"]
            user.save()
        else:
            user.full_name = data["full_name"] or user.full_name
            user.set_password(data["password"])
            user.save()
        membership, _ = Membership.objects.update_or_create(
            organization=invitation.organization,
            user=user,
            defaults={
                "role": invitation.role,
                "role_definition": invitation.role_definition,
                "team": invitation.team,
                "restrict_to_assigned": invitation.restrict_to_assigned,
                "is_active": True,
            },
        )
        membership.assigned_farms.set(invitation.assigned_farms.all())
        membership.assigned_zones.set(invitation.assigned_zones.all())
        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = timezone.now()
        invitation.save(update_fields=["status", "accepted_at", "updated_at"])
        return Response(issue_tokens(user))


class RoleViewSet(TenantQuerySetMixin, PermissionMixin, viewsets.ModelViewSet):
    queryset = RoleDefinition.objects.all()
    serializer_class = RoleDefinitionSerializer
    required_permission = "settings.manage"
    required_read_permission = "members.manage"
    search_fields = ["name", "slug"]

    def perform_create(self, serializer):
        permissions = serializer.validated_data.get("permissions") or []
        unknown = [item for item in permissions if item not in ALL_PERMISSIONS and item != "*"]
        if unknown:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"permissions": f"Unknown permissions: {', '.join(unknown)}"})
        super().perform_create(serializer)


class ApiKeyViewSet(
    TenantQuerySetMixin,
    PermissionMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ApiKey.objects.all()
    serializer_class = ApiKeySerializer
    required_permission = "apikeys.manage"
    required_read_permission = "apikeys.manage"

    def create(self, request, *args, **kwargs):
        self.check_action_permission("apikeys.manage")
        payload = ApiKeyCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        scopes = payload.validated_data["scopes"]
        unknown = [item for item in scopes if item not in ALL_PERMISSIONS and item != "*"]
        if unknown:
            return Response({"scopes": f"Unknown scopes: {', '.join(unknown)}"}, status=400)
        raw, prefix, digest = generate_api_key()
        key = ApiKey.objects.create(
            organization=request.organization,
            name=payload.validated_data["name"],
            prefix=prefix,
            key_hash=digest,
            scopes=scopes,
            created_by=request.user,
            expires_at=payload.validated_data.get("expires_at"),
        )
        data = ApiKeySerializer(key).data
        data["key"] = raw
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        instance.revoked_at = timezone.now()
        instance.save(update_fields=["revoked_at", "updated_at"])


class PermissionCatalogView(APIView):
    required_read_permission = "members.manage"
    required_permission = "settings.manage"

    def get(self, request):
        return Response({"permissions": ALL_PERMISSIONS, "roles": [item[0] for item in SystemRole.CHOICES]})
