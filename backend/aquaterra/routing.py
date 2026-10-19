from django.urls import path

from devices.consumers import TelemetryConsumer
from irrigation.consumers import IrrigationConsumer
from notifications.consumers import NotificationConsumer

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
    path("ws/telemetry/", TelemetryConsumer.as_asgi()),
    path("ws/irrigation/", IrrigationConsumer.as_asgi()),
]
