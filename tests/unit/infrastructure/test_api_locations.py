import pytest
from fastapi.testclient import TestClient
from src.domain.exceptions import LocationNotFoundException
from src.domain.models import Location
from src.domain.value_objects import Coordinates
from src.infrastructure.api.dependencies import (
    get_reverse_geocode_use_case,
    get_search_location_use_case,
)
from src.infrastructure.api.main import app

BOGOTA = Location(name="Bogotá", country="Colombia", coordinates=Coordinates(4.7110, -74.0721))


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


class FakeSearchUseCase:
    def __init__(self, results: list[Location]) -> None:
        self.results = results

    async def execute(self, query: str) -> list[Location]:
        return self.results


class FakeReverseUseCase:
    def __init__(self, result: Location | None = None, raises: Exception | None = None) -> None:
        self.result = result
        self.raises = raises

    async def execute(self, coordinates: Coordinates) -> Location:
        if self.raises is not None:
            raise self.raises
        assert self.result is not None
        return self.result


def test_search_locations_returns_results() -> None:
    app.dependency_overrides[get_search_location_use_case] = lambda: FakeSearchUseCase([BOGOTA])

    with TestClient(app) as client:
        response = client.get("/api/v1/locations/search", params={"q": "Bogota"})

    assert response.status_code == 200
    assert response.json() == [
        {"name": "Bogotá", "country": "Colombia", "latitude": 4.7110, "longitude": -74.0721}
    ]


def test_reverse_geocode_returns_location() -> None:
    app.dependency_overrides[get_reverse_geocode_use_case] = lambda: FakeReverseUseCase(
        result=BOGOTA
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/locations/reverse", params={"lat": 4.71, "lon": -74.07})

    assert response.status_code == 200
    assert response.json()["name"] == "Bogotá"


def test_reverse_geocode_returns_404_when_not_found() -> None:
    app.dependency_overrides[get_reverse_geocode_use_case] = lambda: FakeReverseUseCase(
        raises=LocationNotFoundException("nowhere")
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/locations/reverse", params={"lat": 0, "lon": -140})

    assert response.status_code == 404
