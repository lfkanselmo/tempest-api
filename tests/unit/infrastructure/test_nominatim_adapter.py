import httpx
import pytest
from src.domain.exceptions import LocationNotFoundException
from src.domain.value_objects import Coordinates
from src.infrastructure.providers.nominatim_adapter import NominatimAdapter

COORDINATES = Coordinates(latitude=4.7110, longitude=-74.0721)

FOUND_PAYLOAD = {
    "lat": "4.7109912",
    "lon": "-74.0721413",
    "name": "TransMilenio",
    "display_name": "TransMilenio, Campania, Bogotá, Colombia",
    "address": {
        "city": "Bogotá",
        "country": "Colombia",
        "country_code": "co",
    },
}

FOUND_WITHOUT_CITY_PAYLOAD = {
    "lat": "1.0",
    "lon": "2.0",
    "display_name": "Vereda El Roble, Subachoque, Cundinamarca, Colombia",
    "address": {
        "village": "Vereda El Roble",
        "country": "Colombia",
    },
}

NOT_FOUND_PAYLOAD = {"error": "Unable to geocode"}


def _adapter(handler: httpx.MockTransport) -> NominatimAdapter:
    return NominatimAdapter(httpx.AsyncClient(transport=handler))


@pytest.mark.asyncio
async def test_reverse_maps_response_to_domain() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=FOUND_PAYLOAD))
    adapter = _adapter(transport)

    location = await adapter.reverse(COORDINATES)

    assert location.name == "Bogotá"
    assert location.country == "Colombia"
    assert location.coordinates.latitude == 4.7109912


@pytest.mark.asyncio
async def test_reverse_falls_back_through_address_hierarchy() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json=FOUND_WITHOUT_CITY_PAYLOAD)
    )
    adapter = _adapter(transport)

    location = await adapter.reverse(COORDINATES)

    assert location.name == "Vereda El Roble"


@pytest.mark.asyncio
async def test_reverse_raises_location_not_found_on_error_response() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=NOT_FOUND_PAYLOAD))
    adapter = _adapter(transport)

    with pytest.raises(LocationNotFoundException):
        await adapter.reverse(COORDINATES)
