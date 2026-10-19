from django.urls import include, path
from rest_framework.routers import DefaultRouter

from organizations.views import MembershipViewSet, OrganizationSettingsView, OrganizationViewSet, TeamViewSet

router = DefaultRouter()
router.register("orgs", OrganizationViewSet, basename="organization")
router.register("teams", TeamViewSet, basename="team")
router.register("memberships", MembershipViewSet, basename="membership")

urlpatterns = [
    path("settings/", OrganizationSettingsView.as_view(), name="org-settings"),
    path("", include(router.urls)),
]
