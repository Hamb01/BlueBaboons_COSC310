from pathlib import Path
from typing import Generator
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import get_health_repository, get_health_service
from app.repositories.health_repository import HealthRepository
from app.services.health_service import HealthService


@pytest.fixture
def isolated_data_dir(tmp_path: Path) -> Path:
    """Provides an isolated directory representing the persistence layer."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def isolated_health_repo(isolated_data_dir: Path) -> HealthRepository:
    return HealthRepository(data_dir=isolated_data_dir)


@pytest.fixture
def isolated_health_service(isolated_health_repo: HealthRepository) -> HealthService:
    return HealthService(repository=isolated_health_repo)


@pytest.fixture
def client(
    isolated_health_service: HealthService,
    isolated_health_repo: HealthRepository
) -> Generator[TestClient, None, None]:
    """FastAPI TestClient fixture with dependency overrides for isolated testing."""
    app.dependency_overrides[get_health_repository] = lambda: isolated_health_repo
    app.dependency_overrides[get_health_service] = lambda: isolated_health_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
