from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "AquaTerra"
admin.site.site_title = "AquaTerra"
admin.site.index_title = "Irrigation operations"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/organizations/", include("organizations.urls")),
    path("api/farms/", include("farms.urls")),
    path("api/devices/", include("devices.urls")),
    path("api/irrigation/", include("irrigation.urls")),
    path("api/recommendations/", include("recommendations.urls")),
    path("api/alerts/", include("alerts.urls")),
    path("api/analytics/", include("analytics.urls")),
    path("api/maintenance/", include("maintenance.urls")),
    path("api/work/", include("work.urls")),
    path("api/reports/", include("reports.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/weather/", include("weather.urls")),
    path("api/audit/", include("audit.urls")),
    path("api/search/", include("search.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
