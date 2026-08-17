from fastapi.testclient import TestClient
from src.infrastructure.api.main import app


def test_health_check_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
