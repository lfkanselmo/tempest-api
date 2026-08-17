from typing import Protocol

from src.domain.models import Location
from src.domain.value_objects import Coordinates


class ReverseGeocodingPort(Protocol):
    async def reverse(self, coordinates: Coordinates) -> Location: ...
