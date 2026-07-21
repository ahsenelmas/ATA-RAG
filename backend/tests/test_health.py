from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "ATA RAG"


def test_health_check() -> None:
    response = client.get("/api/health")
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "healthy"
    assert data["service"] == "ata-rag-api"
