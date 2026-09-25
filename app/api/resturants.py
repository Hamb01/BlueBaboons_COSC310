from fastapi import Depends
from app.repositories.health_repository import HealthRepository
from app.services.health_service import HealthService


def get_resturant_repository() -> HealthRepository:
    """Dependency provider for HealthRepository."""
    return HealthRepository()


def get_resturant_service(
    repository: HealthRepository = Depends(get_health_repository)
) -> HealthService:
    """Dependency provider for HealthService with injected repository."""
    return HealthService(repository=repository)
