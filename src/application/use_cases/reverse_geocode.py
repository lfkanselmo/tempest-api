from src.application.ports.reverse_geocoding import ReverseGeocodingPort
from src.domain.models import Location
from src.domain.value_objects import Coordinates


class ReverseGeocodeUseCase:
    def __init__(self, reverse_geocoding: ReverseGeocodingPort) -> None:
        self._reverse_geocoding = reverse_geocoding

    async def execute(self, coordinates: Coordinates) -> Location:
        return await self._reverse_geocoding.reverse(coordinates)
