from typing import cast

from src.application.ports.cache import CachePort
from src.application.ports.reverse_geocoding import ReverseGeocodingPort
from src.domain.models import Location
from src.domain.value_objects import Coordinates

GEOCODING_TTL_SECONDS = 2_592_000


class CachedReverseGeocodingProvider:
    def __init__(self, provider: ReverseGeocodingPort, cache: CachePort) -> None:
        self._provider = provider
        self._cache = cache

    async def reverse(self, coordinates: Coordinates) -> Location:
        key = f"reverse:{coordinates.latitude:.3f}:{coordinates.longitude:.3f}"
        if (cached := await self._cache.get(key)) is not None:
            return cast(Location, cached)

        location = await self._provider.reverse(coordinates)
        await self._cache.set(key, location, GEOCODING_TTL_SECONDS)
        return location
