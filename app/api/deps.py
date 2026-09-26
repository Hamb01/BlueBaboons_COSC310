from fastapi import Depends
from app.repositories.health_repository import HealthRepository
from app.services.health_service import HealthService

from app.repositories.resturant_repository import ResturantRepository
from app.services.resturant_service import ResturantService


def get_health_repository() -> HealthRepository:
    """Dependency provider for HealthRepository."""
    return HealthRepository()


def get_health_service(
    repository: HealthRepository = Depends(get_health_repository)
) -> HealthService:
    """Dependency provider for HealthService with injected repository."""
    return HealthService(repository = repository)


def get_resturant_repository() -> ResturantRepository:
    """Dependency provider for ResturantRepository."""
    return ResturantRepository()

def get_resturant_service(
    repository: ResturantRepository = Depends(get_resturant_repository)
) -> ResturantService:
    """Dependency provider for ResturantService with injected repository."""
    return ResturantService(repository = repository)

