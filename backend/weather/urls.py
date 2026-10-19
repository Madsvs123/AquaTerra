from django.urls import include, path
from rest_framework.routers import DefaultRouter

from weather.views import RefreshWeatherView, WeatherViewSet

router = DefaultRouter()
router.register("observations", WeatherViewSet, basename="weather")

urlpatterns = [
    path("refresh/", RefreshWeatherView.as_view(), name="refresh-weather"),
    path("", include(router.urls)),
]
