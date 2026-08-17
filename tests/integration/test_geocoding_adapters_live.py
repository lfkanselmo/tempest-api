import httpx
import pytest
from src.domain.value_objects import Coordinates
from src.infrastructure.providers.nominatim_adapter import NominatimAdapter
from src.infrastructure.providers.open_meteo_geocoding_adapter import OpenMeteoGeocodingAdapter

BOGOTA_COORDINATES = Coordinates(latitude=4.7110, longitude=-74.0721)

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_search_against_real_open_meteo_geocoding_api() -> None:
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoGeocodingAdapter(client)

        results = await adapter.search("Bogota")

    assert len(results) > 0
    assert any("Bogot" in location.name for location in results)


@pytest.mark.asyncio
async def test_reverse_against_real_nominatim_api() -> None:
    headers = {"User-Agent": "tempest-api-tests (integration test suite)"}
    async with httpx.AsyncClient(headers=headers) as client:
        adapter = NominatimAdapter(client)

        location = await adapter.reverse(BOGOTA_COORDINATES)

    assert location.country == "Colombia"
    assert location.name != ""
