from django.urls import include, path
from rest_framework.routers import DefaultRouter

from work.views import WorkTaskViewSet

router = DefaultRouter()
router.register("tasks", WorkTaskViewSet, basename="task")

urlpatterns = [path("", include(router.urls))]
