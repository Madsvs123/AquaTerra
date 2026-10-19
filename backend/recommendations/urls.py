from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recommendations.views import GenerateRecommendationsView, RecommendationViewSet

router = DefaultRouter()
router.register("items", RecommendationViewSet, basename="recommendation")

urlpatterns = [
    path("generate/", GenerateRecommendationsView.as_view(), name="generate-recommendations"),
    path("", include(router.urls)),
]
