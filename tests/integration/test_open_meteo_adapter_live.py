import httpx
import pytest
from src.domain.value_objects import Coordinates
from src.infrastructure.providers.open_meteo_adapter import OpenMeteoAdapter

BOGOTA = Coordinates(latitude=4.7110, longitude=-74.0721)

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_current_against_real_open_meteo_api() -> None:
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoAdapter(client)

        current = await adapter.get_current(BOGOTA)

    assert -30 <= current.temperature_celsius <= 45
    assert 0 <= current.humidity_percent <= 100
    assert current.wind_speed_kmh >= 0


@pytest.mark.asyncio
async def test_get_forecast_against_real_open_meteo_api() -> None:
    async with httpx.AsyncClient() as client:
        adapter = OpenMeteoAdapter(client)

        forecast = await adapter.get_forecast(BOGOTA)

    assert len(forecast.hourly) > 0
    assert len(forecast.daily) == 7
    assert all(
        entry.temperature_min_celsius <= entry.temperature_max_celsius for entry in forecast.daily
    )
