from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from src.domain.exceptions import FavoriteNotFoundException
from src.domain.models import Favorite, Location
from src.domain.value_objects import Coordinates
from src.infrastructure.api.dependencies import (
    get_add_favorite_use_case,
    get_list_favorites_use_case,
    get_remove_favorite_use_case,
)
from src.infrastructure.api.main import app

BOGOTA_FAVORITE = Favorite(
    id=uuid4(),
    location=Location(name="Bogotá", country="Colombia", coordinates=Coordinates(4.7110, -74.0721)),
    created_at=datetime.now(UTC),
)


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


class FakeListUseCase:
    def __init__(self, favorites: list[Favorite]) -> None:
        self.favorites = favorites

    def execute(self) -> list[Favorite]:
        return self.favorites


class FakeAddUseCase:
    def __init__(self, result: Favorite) -> None:
        self.result = result

    def execute(self, location: Location) -> Favorite:
        return self.result


class FakeRemoveUseCase:
    def __init__(self, raises: Exception | None = None) -> None:
        self.raises = raises

    def execute(self, favorite_id: UUID) -> None:
        if self.raises is not None:
            raise self.raises


def test_list_favorites_returns_all() -> None:
    app.dependency_overrides[get_list_favorites_use_case] = lambda: FakeListUseCase(
        [BOGOTA_FAVORITE]
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/favorites")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Bogotá"


def test_add_favorite_returns_created_favorite() -> None:
    app.dependency_overrides[get_add_favorite_use_case] = lambda: FakeAddUseCase(BOGOTA_FAVORITE)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/favorites",
            json={
                "name": "Bogotá",
                "country": "Colombia",
                "latitude": 4.7110,
                "longitude": -74.0721,
            },
        )

    assert response.status_code == 201
    assert response.json()["name"] == "Bogotá"


def test_remove_favorite_returns_204() -> None:
    app.dependency_overrides[get_remove_favorite_use_case] = lambda: FakeRemoveUseCase()

    with TestClient(app) as client:
        response = client.delete(f"/api/v1/favorites/{uuid4()}")

    assert response.status_code == 204


def test_remove_favorite_returns_404_when_not_found() -> None:
    app.dependency_overrides[get_remove_favorite_use_case] = lambda: FakeRemoveUseCase(
        raises=FavoriteNotFoundException("missing")
    )

    with TestClient(app) as client:
        response = client.delete(f"/api/v1/favorites/{uuid4()}")

    assert response.status_code == 404
