from fastapi import Depends
from app.repositories.health_repository import HealthRepository
from app.services.health_service import HealthService
from app.repositories.restaurant_repository import RestaurantRepository
# from app.services.restaurant_service import RestaurantService


def get_health_repository() -> HealthRepository:
    """Dependency provider for HealthRepository."""
    return HealthRepository()


def get_health_service(
    repository: HealthRepository = Depends(get_health_repository)
) -> HealthService:
    """Dependency provider for HealthService with injected repository."""
    return HealthService(repository=repository)

def get_restaurant_repository() -> RestaurantRepository:
    """Dependency provider for RestaurantRepository."""
    return RestaurantRepository()

# Uncomment next block prior to restaurant service testing (or imediately after implementation of restaurant_service.py)

# def get_restaurant_service(
#     repository: RestaurantRepository = Depends(get_restaurant_repository)
# ) -> RestaurantService:
#     """Dependency provider for RestaurantService with injected repository."""
#     return RestaurantService(repository=repository)
