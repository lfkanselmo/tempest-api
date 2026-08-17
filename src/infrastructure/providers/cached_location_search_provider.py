from typing import cast

from src.application.ports.cache import CachePort
from src.application.ports.location_search import LocationSearchPort
from src.domain.models import Location

GEOCODING_TTL_SECONDS = 2_592_000


class CachedLocationSearchProvider:
    def __init__(self, provider: LocationSearchPort, cache: CachePort) -> None:
        self._provider = provider
        self._cache = cache

    async def search(self, query: str) -> list[Location]:
        key = f"search:{query.strip().lower()}"
        if (cached := await self._cache.get(key)) is not None:
            return cast(list[Location], cached)

        results = await self._provider.search(query)
        await self._cache.set(key, results, GEOCODING_TTL_SECONDS)
        return results
