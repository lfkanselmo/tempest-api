import httpx
import pytest
from src.infrastructure.providers.open_meteo_geocoding_adapter import OpenMeteoGeocodingAdapter

FOUND_PAYLOAD = {
    "results": [
        {"name": "Bogotá", "country": "Colombia", "latitude": 4.60971, "longitude": -74.08175},
        {
            "name": "Bogota",
            "country": "Estados Unidos",
            "latitude": 40.87621,
            "longitude": -74.02986,
        },
    ]
}

NOT_FOUND_PAYLOAD = {"generationtime_ms": 0.2}


def _adapter(handler: httpx.MockTransport) -> OpenMeteoGeocodingAdapter:
    return OpenMeteoGeocodingAdapter(httpx.AsyncClient(transport=handler))


@pytest.mark.asyncio
async def test_search_maps_results_to_domain() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=FOUND_PAYLOAD))
    adapter = _adapter(transport)

    locations = await adapter.search("Bogota")

    assert len(locations) == 2
    assert locations[0].name == "Bogotá"
    assert locations[0].country == "Colombia"
    assert locations[0].coordinates.latitude == 4.60971


@pytest.mark.asyncio
async def test_search_returns_empty_list_when_no_results() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=NOT_FOUND_PAYLOAD))
    adapter = _adapter(transport)

    locations = await adapter.search("zzzznonexistentplace")

    assert locations == []
