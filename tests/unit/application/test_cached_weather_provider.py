from datetime import UTC, datetime

import pytest
from src.domain.exceptions import ProviderUnavailableException
from src.domain.models import CurrentConditions
from src.domain.value_objects import Coordinates, WeatherCondition
from src.infrastructure.providers.cached_weather_provider import (
    CURRENT_TTL_SECONDS,
    CachedWeatherProvider,
)

COORDINATES = Coordinates(latitude=4.7110, longitude=-74.0721)
CURRENT_CACHE_KEY = "current:4.7110:-74.0721"

CURRENT = CurrentConditions(
    temperature_celsius=20.0,
    apparent_temperature_celsius=19.5,
    condition=WeatherCondition.CLEAR,
    is_day=True,
    humidity_percent=50,
    wind_speed_kmh=10.0,
    precipitation_mm=0.0,
    pressure_hpa=1013.0,
    uv_index=5.0,
    sunrise=datetime.now(UTC),
    sunset=datetime.now(UTC),
    observed_at=datetime.now(UTC),
)


class FakeCache:
    def __init__(self) -> None:
        self._fresh: dict[str, object] = {}
        self._all: dict[str, object] = {}
        self.set_calls: list[tuple[str, object, int]] = []

    async def get(self, key: str) -> object | None:
        return self._fresh.get(key)

    async def get_stale(self, key: str) -> object | None:
        return self._all.get(key)

    async def set(self, key: str, value: object, ttl_seconds: int) -> None:
        self._fresh[key] = value
        self._all[key] = value
        self.set_calls.append((key, value, ttl_seconds))

    def expire(self, key: str) -> None:
        self._fresh.pop(key, None)


class FakeWeatherProvider:
    def __init__(
        self,
        current: CurrentConditions | None = None,
        raises: Exception | None = None,
    ) -> None:
        self.current = current
        self.raises = raises
        self.calls = 0

    async def get_current(self, coordinates: Coordinates) -> CurrentConditions:
        self.calls += 1
        if self.raises is not None:
            raise self.raises
        assert self.current is not None
        return self.current

    async def get_forecast(self, coordinates: Coordinates) -> None:  # type: ignore[override]
        raise NotImplementedError


@pytest.mark.asyncio
async def test_fetches_and_caches_on_miss() -> None:
    cache = FakeCache()
    provider = FakeWeatherProvider(current=CURRENT)
    cached_provider = CachedWeatherProvider(provider, cache)

    result = await cached_provider.get_current(COORDINATES)

    assert result == CURRENT
    assert provider.calls == 1
    assert cache.set_calls == [(CURRENT_CACHE_KEY, CURRENT, CURRENT_TTL_SECONDS)]


@pytest.mark.asyncio
async def test_returns_cached_value_without_calling_provider_again() -> None:
    cache = FakeCache()
    provider = FakeWeatherProvider(current=CURRENT)
    cached_provider = CachedWeatherProvider(provider, cache)
    await cached_provider.get_current(COORDINATES)

    result = await cached_provider.get_current(COORDINATES)

    assert result == CURRENT
    assert provider.calls == 1


@pytest.mark.asyncio
async def test_serves_stale_value_when_provider_unavailable() -> None:
    cache = FakeCache()
    provider = FakeWeatherProvider(current=CURRENT)
    cached_provider = CachedWeatherProvider(provider, cache)
    await cached_provider.get_current(COORDINATES)
    cache.expire(CURRENT_CACHE_KEY)
    provider.raises = ProviderUnavailableException("down")

    result = await cached_provider.get_current(COORDINATES)

    assert result.is_stale is True
    assert result.temperature_celsius == CURRENT.temperature_celsius


@pytest.mark.asyncio
async def test_raises_when_provider_unavailable_and_nothing_cached() -> None:
    cache = FakeCache()
    provider = FakeWeatherProvider(raises=ProviderUnavailableException("down"))
    cached_provider = CachedWeatherProvider(provider, cache)

    with pytest.raises(ProviderUnavailableException):
        await cached_provider.get_current(COORDINATES)
