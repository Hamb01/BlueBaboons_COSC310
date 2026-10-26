from fastapi import Depends
from app.repositories.health_repository import HealthRepository
from app.services.health_service import HealthService

from app.repositories.restaurant_repository import RestaurantRepository
from app.services.restaurant_service import RestaurantService

from app.repositories.menu_repository import MenuRepository
from app.services.menu_service import MenuService


def get_health_repository() -> HealthRepository:
    """Dependency provider for HealthRepository."""
    return HealthRepository()


def get_health_service(
    repository: HealthRepository = Depends(get_health_repository)
) -> HealthService:
    """Dependency provider for HealthService with injected repository."""
    return HealthService(repository = repository)


def get_restaurant_repository() -> RestaurantRepository:
    """Dependency provider for RestaurantRepository."""
    return RestaurantRepository()

def get_restaurant_service(
    repository: RestaurantRepository = Depends(get_restaurant_repository)
) -> RestaurantService:
    """Dependency provider for RestaurantService with injected repository."""
    return RestaurantService(repository=repository)


def get_menu_repository(
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository)
) -> MenuRepository:
    """Dependency provider for MenuRepository, sharing the request's RestaurantRepository."""
    return MenuRepository(restaurant_repository=restaurant_repository)

def get_menu_service(
    repository: MenuRepository = Depends(get_menu_repository)
) -> MenuService:
    """Dependency provider for MenuService with injected repository."""
    return MenuService(repository=repository)
