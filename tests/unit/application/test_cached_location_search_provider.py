import pytest
from src.domain.models import Location
from src.domain.value_objects import Coordinates
from src.infrastructure.providers.cached_location_search_provider import (
    CachedLocationSearchProvider,
)

BOGOTA = [Location(name="Bogotá", country="Colombia", coordinates=Coordinates(4.7110, -74.0721))]


class FakeCache:
    def __init__(self) -> None:
        self.store: dict[str, object] = {}
        self.set_calls: list[tuple[str, object, int]] = []

    async def get(self, key: str) -> object | None:
        return self.store.get(key)

    async def get_stale(self, key: str) -> object | None:
        return self.store.get(key)

    async def set(self, key: str, value: object, ttl_seconds: int) -> None:
        self.store[key] = value
        self.set_calls.append((key, value, ttl_seconds))


class FakeLocationSearchProvider:
    def __init__(self, results: list[Location]) -> None:
        self.results = results
        self.calls = 0

    async def search(self, query: str) -> list[Location]:
        self.calls += 1
        return self.results


@pytest.mark.asyncio
async def test_fetches_and_caches_on_miss() -> None:
    cache = FakeCache()
    provider = FakeLocationSearchProvider(BOGOTA)
    cached_provider = CachedLocationSearchProvider(provider, cache)

    result = await cached_provider.search("Bogota")

    assert result == BOGOTA
    assert provider.calls == 1
    assert len(cache.set_calls) == 1


@pytest.mark.asyncio
async def test_returns_cached_results_without_calling_provider_again() -> None:
    cache = FakeCache()
    provider = FakeLocationSearchProvider(BOGOTA)
    cached_provider = CachedLocationSearchProvider(provider, cache)
    await cached_provider.search("Bogota")

    await cached_provider.search("  BOGOTA  ")

    assert provider.calls == 1
