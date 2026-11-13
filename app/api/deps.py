"""Dependency wiring for repositories and services used throughout the API."""

from fastapi import Depends

from app.repositories.health_repository import HealthRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository
from app.services.health_service import HealthService
from app.services.menu_service import MenuService
from app.services.restaurant_service import RestaurantService
from app.services.user_service import UserService



def get_health_repository() -> HealthRepository:
    """Build a health repository instance for dependency injection."""
    return HealthRepository()


def get_health_service(
    repository: HealthRepository = Depends(get_health_repository),
) -> HealthService:
    """Provide a health service backed by the repository dependency."""
    return HealthService(repository=repository)


def get_restaurant_repository() -> RestaurantRepository:
    """Build a restaurant repository instance for dependency injection."""
    return RestaurantRepository()


def get_restaurant_service(
    repository: RestaurantRepository = Depends(get_restaurant_repository),
) -> RestaurantService:
    """Provide a restaurant service backed by the repository dependency."""
    return RestaurantService(repository=repository)


def get_menu_repository(
    restaurant_repository: RestaurantRepository = Depends(get_restaurant_repository),
) -> MenuRepository:
    """Provide a menu repository that shares the request restaurant repository."""
    return MenuRepository(restaurant_repository=restaurant_repository)


def get_menu_service(
    repository: MenuRepository = Depends(get_menu_repository),
) -> MenuService:
    """Provide a menu service backed by the repository dependency."""
    return MenuService(repository=repository)

def get_user_repository() -> UserRepository:
    """Build a user repository instance for dependency injection."""
    return UserRepository


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Provide a user service backed by the repository dependency."""
    return UserService(repository=repository)
