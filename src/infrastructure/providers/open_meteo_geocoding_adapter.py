import httpx

from src.domain.exceptions import ProviderUnavailableException
from src.domain.models import Location
from src.domain.value_objects import Coordinates
from src.infrastructure.providers.open_meteo_geocoding_schemas import (
    OpenMeteoGeocodingResponse,
)

SEARCH_URL = "https://geocoding-api.open-meteo.com/v1/search"


class OpenMeteoGeocodingAdapter:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def search(self, query: str) -> list[Location]:
        try:
            response = await self._client.get(
                SEARCH_URL, params={"name": query, "count": 10, "language": "es"}
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise ProviderUnavailableException(str(error)) from error

        parsed = OpenMeteoGeocodingResponse.model_validate(response.json())
        return [
            Location(
                name=result.name,
                country=result.country,
                coordinates=Coordinates(latitude=result.latitude, longitude=result.longitude),
            )
            for result in parsed.results
        ]
