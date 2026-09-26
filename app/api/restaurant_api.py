from fastapi import Depends
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.restaurant_service import RestaurantService


def get_restaurant_repository() -> RestaurantRepository:
    """Dependency provider for RestaurantRepository."""
    return RestaurantRepository()


def get_restaurant_service(
    repository: RestaurantRepository = Depends(get_restaurant_repository)
) -> RestaurantService:
    """Dependency provider for RestaurantService with injected repository."""
    return RestaurantService(repository=repository)
