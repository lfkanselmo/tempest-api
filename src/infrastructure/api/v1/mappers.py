from src.domain.models import (
    CurrentConditions,
    DailyForecastEntry,
    Favorite,
    Forecast,
    HourlyForecastEntry,
    Location,
)
from src.infrastructure.api.v1.schemas import (
    CurrentConditionsOut,
    DailyForecastEntryOut,
    FavoriteOut,
    ForecastOut,
    HourlyForecastEntryOut,
    LocationOut,
)


def to_location_out(location: Location) -> LocationOut:
    return LocationOut(
        name=location.name,
        country=location.country,
        latitude=location.coordinates.latitude,
        longitude=location.coordinates.longitude,
    )


def to_current_conditions_out(conditions: CurrentConditions) -> CurrentConditionsOut:
    return CurrentConditionsOut(
        temperature_celsius=conditions.temperature_celsius,
        apparent_temperature_celsius=conditions.apparent_temperature_celsius,
        condition=conditions.condition,
        is_day=conditions.is_day,
        humidity_percent=conditions.humidity_percent,
        wind_speed_kmh=conditions.wind_speed_kmh,
        precipitation_mm=conditions.precipitation_mm,
        pressure_hpa=conditions.pressure_hpa,
        uv_index=conditions.uv_index,
        sunrise=conditions.sunrise,
        sunset=conditions.sunset,
        observed_at=conditions.observed_at,
        is_stale=conditions.is_stale,
    )


def to_forecast_out(forecast: Forecast) -> ForecastOut:
    return ForecastOut(
        hourly=[_to_hourly_out(entry) for entry in forecast.hourly],
        daily=[_to_daily_out(entry) for entry in forecast.daily],
        is_stale=forecast.is_stale,
    )


def _to_hourly_out(entry: HourlyForecastEntry) -> HourlyForecastEntryOut:
    return HourlyForecastEntryOut(
        timestamp=entry.timestamp,
        temperature_celsius=entry.temperature_celsius,
        condition=entry.condition,
        precipitation_probability_percent=entry.precipitation_probability_percent,
    )


def _to_daily_out(entry: DailyForecastEntry) -> DailyForecastEntryOut:
    return DailyForecastEntryOut(
        date=entry.date,
        temperature_min_celsius=entry.temperature_min_celsius,
        temperature_max_celsius=entry.temperature_max_celsius,
        condition=entry.condition,
        precipitation_probability_percent=entry.precipitation_probability_percent,
    )


def to_favorite_out(favorite: Favorite) -> FavoriteOut:
    return FavoriteOut(
        id=favorite.id,
        name=favorite.location.name,
        country=favorite.location.country,
        latitude=favorite.location.coordinates.latitude,
        longitude=favorite.location.coordinates.longitude,
        created_at=favorite.created_at,
    )
