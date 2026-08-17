from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from src.domain.exceptions import ProviderUnavailableException
from src.domain.models import CurrentConditions, Forecast
from src.domain.value_objects import Coordinates, WeatherCondition
from src.infrastructure.api.dependencies import (
    get_current_weather_use_case,
    get_forecast_use_case,
)
from src.infrastructure.api.main import app

CURRENT = CurrentConditions(
    temperature_celsius=20.0,
    apparent_temperature_celsius=19.5,
    condition=WeatherCondition.CLEAR,
    is_day=True,
    humidity_percent=50,
    wind_speed_kmh=10.0,
    precipitation_mm=0.0,
    observed_at=datetime.now(UTC),
)

FORECAST = Forecast(hourly=(), daily=())


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


class FakeUseCase:
    def __init__(self, result: object = None, raises: Exception | None = None) -> None:
        self.result = result
        self.raises = raises

    async def execute(self, coordinates: Coordinates) -> object:
        if self.raises is not None:
            raise self.raises
        return self.result


def test_get_current_weather_returns_conditions() -> None:
    app.dependency_overrides[get_current_weather_use_case] = lambda: FakeUseCase(result=CURRENT)

    with TestClient(app) as client:
        response = client.get("/api/v1/weather/current", params={"lat": 4.71, "lon": -74.07})

    assert response.status_code == 200
    body = response.json()
    assert body["temperature_celsius"] == 20.0
    assert body["condition"] == "clear"


def test_get_current_weather_rejects_invalid_latitude() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/weather/current", params={"lat": 999, "lon": 0})

    assert response.status_code == 422


def test_get_current_weather_returns_503_when_provider_unavailable() -> None:
    app.dependency_overrides[get_current_weather_use_case] = lambda: FakeUseCase(
        raises=ProviderUnavailableException("down")
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/weather/current", params={"lat": 4.71, "lon": -74.07})

    assert response.status_code == 503


def test_get_forecast_returns_forecast() -> None:
    app.dependency_overrides[get_forecast_use_case] = lambda: FakeUseCase(result=FORECAST)

    with TestClient(app) as client:
        response = client.get("/api/v1/weather/forecast", params={"lat": 4.71, "lon": -74.07})

    assert response.status_code == 200
    assert response.json() == {"hourly": [], "daily": [], "is_stale": False}
