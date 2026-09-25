from pathlib import Path
from fastapi.testclient import TestClient
from app.repositories.health_repository import HealthRepository
from app.services.health_service import HealthService


def test_health_check_returns_200_and_ok(client: TestClient):
    """Verify that GET /health returns HTTP 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["persistence"] == "connected"
    assert "app_name" in data
    assert "version" in data


def test_root_overview_returns_200(client: TestClient):
    """Verify root endpoint provides links to documentation and health check."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["health_check"] == "/health"
    assert data["documentation"] == "/docs"


def test_health_repository_missing_dir(tmp_path: Path):
    """Test repository behavior when persistence directory is missing."""
    missing_dir = tmp_path / "nonexistent_dir"
    repo = HealthRepository(data_dir=missing_dir)
    status = repo.check_persistence()
    assert status["status"] == "uninitialized"


def test_health_service_layer(isolated_health_repo: HealthRepository):
    """Test service layer coordinates correctly with repository."""
    service = HealthService(repository=isolated_health_repo)
    result = service.get_health_status()
    assert result.status == "ok"
    assert result.persistence == "connected"


def test_invalid_endpoint_returns_404(client: TestClient):
    """Failure test: Verify non-existent route returns HTTP 404."""
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404
