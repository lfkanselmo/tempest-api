import dataclasses
from typing import cast

from src.application.ports.cache import CachePort
from src.application.ports.weather_provider import WeatherProviderPort
from src.domain.exceptions import ProviderUnavailableException
from src.domain.models import CurrentConditions, Forecast
from src.domain.value_objects import Coordinates

CURRENT_TTL_SECONDS = 600
FORECAST_TTL_SECONDS = 1_800


class CachedWeatherProvider:
    def __init__(self, provider: WeatherProviderPort, cache: CachePort) -> None:
        self._provider = provider
        self._cache = cache

    async def get_current(self, coordinates: Coordinates) -> CurrentConditions:
        key = self._key("current", coordinates)
        if (cached := await self._cache.get(key)) is not None:
            return cast(CurrentConditions, cached)

        try:
            fresh = await self._provider.get_current(coordinates)
        except ProviderUnavailableException:
            stale = await self._cache.get_stale(key)
            if stale is not None:
                return dataclasses.replace(cast(CurrentConditions, stale), is_stale=True)
            raise

        await self._cache.set(key, fresh, CURRENT_TTL_SECONDS)
        return fresh

    async def get_forecast(self, coordinates: Coordinates) -> Forecast:
        key = self._key("forecast", coordinates)
        if (cached := await self._cache.get(key)) is not None:
            return cast(Forecast, cached)

        try:
            fresh = await self._provider.get_forecast(coordinates)
        except ProviderUnavailableException:
            stale = await self._cache.get_stale(key)
            if stale is not None:
                return dataclasses.replace(cast(Forecast, stale), is_stale=True)
            raise

        await self._cache.set(key, fresh, FORECAST_TTL_SECONDS)
        return fresh

    @staticmethod
    def _key(prefix: str, coordinates: Coordinates) -> str:
        return f"{prefix}:{coordinates.latitude:.4f}:{coordinates.longitude:.4f}"
