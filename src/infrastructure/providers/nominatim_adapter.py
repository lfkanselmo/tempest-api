import httpx

from src.domain.exceptions import LocationNotFoundException, ProviderUnavailableException
from src.domain.models import Location
from src.domain.value_objects import Coordinates
from src.infrastructure.providers.nominatim_schemas import NominatimReverseResponse

REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"


class NominatimAdapter:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def reverse(self, coordinates: Coordinates) -> Location:
        try:
            response = await self._client.get(
                REVERSE_URL,
                params={
                    "lat": coordinates.latitude,
                    "lon": coordinates.longitude,
                    "format": "jsonv2",
                    "accept-language": "es",
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise ProviderUnavailableException(str(error)) from error

        payload = response.json()
        if "error" in payload:
            raise LocationNotFoundException(str(coordinates))

        parsed = NominatimReverseResponse.model_validate(payload)
        return Location(
            name=self._resolve_name(parsed),
            country=parsed.address.country or "",
            coordinates=Coordinates(latitude=parsed.lat, longitude=parsed.lon),
        )

    @staticmethod
    def _resolve_name(parsed: NominatimReverseResponse) -> str:
        address = parsed.address
        return (
            address.city
            or address.town
            or address.village
            or address.municipality
            or address.county
            or parsed.display_name.split(",")[0].strip()
        )
