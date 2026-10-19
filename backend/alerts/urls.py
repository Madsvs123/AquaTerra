from django.urls import include, path
from rest_framework.routers import DefaultRouter

from alerts.views import AlertRuleViewSet, AlertViewSet, EvaluateAlertsView

router = DefaultRouter()
router.register("rules", AlertRuleViewSet, basename="alert-rule")
router.register("events", AlertViewSet, basename="alert")

urlpatterns = [
    path("evaluate/", EvaluateAlertsView.as_view(), name="evaluate-alerts"),
    path("", include(router.urls)),
]
