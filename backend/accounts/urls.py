from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import (
    AcceptInviteView,
    ApiKeyViewSet,
    InvitationViewSet,
    LoginView,
    LogoutView,
    MeView,
    PermissionCatalogView,
    RefreshView,
    RegisterView,
    RoleViewSet,
)

router = DefaultRouter()
router.register("invitations", InvitationViewSet, basename="invitation")
router.register("api-keys", ApiKeyViewSet, basename="apikey")
router.register("roles", RoleViewSet, basename="role")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("invitations/accept/", AcceptInviteView.as_view(), name="accept-invite"),
    path("permissions/", PermissionCatalogView.as_view(), name="permission-catalog"),
    path("", include(router.urls)),
]
