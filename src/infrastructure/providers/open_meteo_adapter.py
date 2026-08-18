import httpx

from src.domain.exceptions import ProviderUnavailableException
from src.domain.models import CurrentConditions, DailyForecastEntry, Forecast, HourlyForecastEntry
from src.domain.value_objects import Coordinates
from src.infrastructure.providers.open_meteo_condition_mapper import map_wmo_code
from src.infrastructure.providers.open_meteo_schemas import (
    OpenMeteoCurrentResponse,
    OpenMeteoForecastResponse,
)

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

CURRENT_FIELDS = (
    "temperature_2m,apparent_temperature,relative_humidity_2m,is_day,precipitation,"
    "weather_code,wind_speed_10m,surface_pressure"
)
CURRENT_DAILY_FIELDS = "sunrise,sunset,uv_index_max"
HOURLY_FIELDS = "temperature_2m,precipitation_probability,weather_code"
DAILY_FIELDS = "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max"


class OpenMeteoAdapter:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def get_current(self, coordinates: Coordinates) -> CurrentConditions:
        payload = await self._request(
            {
                "latitude": coordinates.latitude,
                "longitude": coordinates.longitude,
                "current": CURRENT_FIELDS,
                "daily": CURRENT_DAILY_FIELDS,
                "forecast_days": 1,
                "timezone": "auto",
            }
        )
        response = OpenMeteoCurrentResponse.model_validate(payload)
        return self._to_current_conditions(response)

    async def get_forecast(self, coordinates: Coordinates) -> Forecast:
        payload = await self._request(
            {
                "latitude": coordinates.latitude,
                "longitude": coordinates.longitude,
                "hourly": HOURLY_FIELDS,
                "daily": DAILY_FIELDS,
                "timezone": "auto",
            }
        )
        response = OpenMeteoForecastResponse.model_validate(payload)
        return self._to_forecast(response)

    async def _request(self, params: dict[str, str | float | int]) -> dict[str, object]:
        try:
            response = await self._client.get(FORECAST_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise ProviderUnavailableException(str(error)) from error
        result: dict[str, object] = response.json()
        return result

    @staticmethod
    def _to_current_conditions(response: OpenMeteoCurrentResponse) -> CurrentConditions:
        current = response.current
        daily = response.daily
        return CurrentConditions(
            temperature_celsius=current.temperature_2m,
            apparent_temperature_celsius=current.apparent_temperature,
            condition=map_wmo_code(current.weather_code),
            is_day=current.is_day == 1,
            humidity_percent=current.relative_humidity_2m,
            wind_speed_kmh=current.wind_speed_10m,
            precipitation_mm=current.precipitation,
            pressure_hpa=current.surface_pressure,
            uv_index=daily.uv_index_max[0],
            sunrise=daily.sunrise[0],
            sunset=daily.sunset[0],
            observed_at=current.time,
        )

    @classmethod
    def _to_forecast(cls, response: OpenMeteoForecastResponse) -> Forecast:
        return Forecast(
            hourly=cls._to_hourly_entries(response),
            daily=cls._to_daily_entries(response),
        )

    @staticmethod
    def _to_hourly_entries(
        response: OpenMeteoForecastResponse,
    ) -> tuple[HourlyForecastEntry, ...]:
        return tuple(
            HourlyForecastEntry(
                timestamp=timestamp,
                temperature_celsius=temperature,
                condition=map_wmo_code(code),
                precipitation_probability_percent=probability,
            )
            for timestamp, temperature, probability, code in zip(
                response.hourly.time,
                response.hourly.temperature_2m,
                response.hourly.precipitation_probability,
                response.hourly.weather_code,
                strict=True,
            )
        )

    @staticmethod
    def _to_daily_entries(
        response: OpenMeteoForecastResponse,
    ) -> tuple[DailyForecastEntry, ...]:
        return tuple(
            DailyForecastEntry(
                date=day,
                temperature_min_celsius=temp_min,
                temperature_max_celsius=temp_max,
                condition=map_wmo_code(code),
                precipitation_probability_percent=probability,
            )
            for day, temp_min, temp_max, probability, code in zip(
                response.daily.time,
                response.daily.temperature_2m_min,
                response.daily.temperature_2m_max,
                response.daily.precipitation_probability_max,
                response.daily.weather_code,
                strict=True,
            )
        )
