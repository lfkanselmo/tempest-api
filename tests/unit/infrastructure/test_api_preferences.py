import pytest
from fastapi.testclient import TestClient
from src.domain.value_objects import UnitSystem
from src.infrastructure.api.dependencies import (
    get_get_preferences_use_case,
    get_set_preferences_use_case,
)
from src.infrastructure.api.main import app


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


class FakeGetUseCase:
    def __init__(self, result: UnitSystem) -> None:
        self.result = result

    def execute(self) -> UnitSystem:
        return self.result


class FakeSetUseCase:
    def __init__(self) -> None:
        self.received: UnitSystem | None = None

    def execute(self, unit_system: UnitSystem) -> None:
        self.received = unit_system


def test_get_preferences_returns_unit_system() -> None:
    app.dependency_overrides[get_get_preferences_use_case] = lambda: FakeGetUseCase(
        UnitSystem.METRIC
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/preferences")

    assert response.status_code == 200
    assert response.json() == {"unit_system": "metric"}


def test_update_preferences_returns_new_value() -> None:
    fake_use_case = FakeSetUseCase()
    app.dependency_overrides[get_set_preferences_use_case] = lambda: fake_use_case

    with TestClient(app) as client:
        response = client.put("/api/v1/preferences", json={"unit_system": "imperial"})

    assert response.status_code == 200
    assert response.json() == {"unit_system": "imperial"}
    assert fake_use_case.received == UnitSystem.IMPERIAL
