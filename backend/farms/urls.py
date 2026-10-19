from django.urls import include, path
from rest_framework.routers import DefaultRouter

from farms.views import FarmViewSet, FieldViewSet, IrrigationZoneViewSet, SiteViewSet

router = DefaultRouter()
router.register("farms", FarmViewSet, basename="farm")
router.register("sites", SiteViewSet, basename="site")
router.register("fields", FieldViewSet, basename="field")
router.register("zones", IrrigationZoneViewSet, basename="zone")

urlpatterns = [path("", include(router.urls))]
