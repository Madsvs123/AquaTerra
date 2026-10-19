from django.db import models

from common.models import DecimalMeasure, TenantOwnedModel


class WeatherObservation(TenantOwnedModel):
    farm = models.ForeignKey("farms.Farm", on_delete=models.CASCADE, related_name="weather")
    observed_at = models.DateTimeField()
    temperature_c = DecimalMeasure()
    humidity = DecimalMeasure()
    precipitation_mm = DecimalMeasure()
    wind_kph = DecimalMeasure()
    et0_mm = DecimalMeasure()
    condition = models.CharField(max_length=80, blank=True)
    source = models.CharField(max_length=40, default="open-meteo")

    class Meta:
        ordering = ["-observed_at"]
        indexes = [models.Index(fields=["organization", "farm", "observed_at"])]
