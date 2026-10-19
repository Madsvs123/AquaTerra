from datetime import timezone as dt_timezone

import httpx
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from weather.models import WeatherObservation


def refresh_farm_weather(farm):
    if farm.latitude is None or farm.longitude is None:
        return None
    params = {
        "latitude": float(farm.latitude),
        "longitude": float(farm.longitude),
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,et0_fao_evapotranspiration",
        "timezone": "UTC",
    }
    try:
        response = httpx.get(settings.WEATHER_API_URL, params=params, timeout=12)
        response.raise_for_status()
        current = response.json().get("current") or {}
    except Exception:
        return None
    observed = parse_datetime(current.get("time")) if current.get("time") else timezone.now()
    if observed and timezone.is_naive(observed):
        observed = timezone.make_aware(observed, dt_timezone.utc)
    return WeatherObservation.objects.create(
        organization=farm.organization,
        farm=farm,
        observed_at=observed or timezone.now(),
        temperature_c=current.get("temperature_2m"),
        humidity=current.get("relative_humidity_2m"),
        precipitation_mm=current.get("precipitation"),
        wind_kph=current.get("wind_speed_10m"),
        et0_mm=current.get("et0_fao_evapotranspiration"),
        condition="rain" if float(current.get("precipitation") or 0) > 0 else "clear",
        source="open-meteo",
    )
