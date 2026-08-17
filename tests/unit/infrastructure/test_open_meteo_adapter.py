import httpx
import pytest
from src.domain.exceptions import ProviderUnavailableException
from src.domain.value_objects import Coordinates, WeatherCondition
from src.infrastructure.providers.open_meteo_adapter import OpenMeteoAdapter

COORDINATES = Coordinates(latitude=4.7110, longitude=-74.0721)

CURRENT_PAYLOAD = {
    "current": {
        "time": "2026-08-16T22:45",
        "temperature_2m": 13.6,
        "apparent_temperature": 13.9,
        "relative_humidity_2m": 93,
        "is_day": 0,
        "precipitation": 0.3,
        "weather_code": 55,
        "wind_speed_10m": 3.1,
    }
}

FORECAST_PAYLOAD = {
    "hourly": {
        "time": ["2026-08-16T00:00", "2026-08-16T01:00"],
        "temperature_2m": [14.8, 15.2],
        "precipitation_probability": [10, 20],
        "weather_code": [1, 2],
    },
    "daily": {
        "time": ["2026-08-16", "2026-08-17"],
        "temperature_2m_max": [22.0, 21.4],
        "temperature_2m_min": [12.3, 12.7],
        "precipitation_probability_max": [30, 40],
        "weather_code": [61, 3],
    },
}


def _adapter(handler: httpx.MockTransport) -> OpenMeteoAdapter:
    client = httpx.AsyncClient(transport=handler)
    return OpenMeteoAdapter(client)


@pytest.mark.asyncio
async def test_get_current_maps_response_to_domain() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=CURRENT_PAYLOAD))
    adapter = _adapter(transport)

    current = await adapter.get_current(COORDINATES)

    assert current.temperature_celsius == 13.6
    assert current.apparent_temperature_celsius == 13.9
    assert current.humidity_percent == 93
    assert current.is_day is False
    assert current.precipitation_mm == 0.3
    assert current.wind_speed_kmh == 3.1
    assert current.condition == WeatherCondition.DRIZZLE


@pytest.mark.asyncio
async def test_get_forecast_maps_response_to_domain() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=FORECAST_PAYLOAD))
    adapter = _adapter(transport)

    forecast = await adapter.get_forecast(COORDINATES)

    assert len(forecast.hourly) == 2
    assert forecast.hourly[0].temperature_celsius == 14.8
    assert forecast.hourly[0].condition == WeatherCondition.CLEAR
    assert forecast.hourly[1].condition == WeatherCondition.PARTLY_CLOUDY

    assert len(forecast.daily) == 2
    assert forecast.daily[0].temperature_max_celsius == 22.0
    assert forecast.daily[0].condition == WeatherCondition.RAIN
    assert forecast.daily[1].condition == WeatherCondition.CLOUDY


@pytest.mark.asyncio
async def test_raises_provider_unavailable_on_http_error() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(503))
    adapter = _adapter(transport)

    with pytest.raises(ProviderUnavailableException):
        await adapter.get_current(COORDINATES)


@pytest.mark.asyncio
async def test_raises_provider_unavailable_on_network_error() -> None:
    def raise_network_error(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    transport = httpx.MockTransport(raise_network_error)
    adapter = _adapter(transport)

    with pytest.raises(ProviderUnavailableException):
        await adapter.get_current(COORDINATES)
