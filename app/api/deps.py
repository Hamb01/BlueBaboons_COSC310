"""Dependency wiring for repositories and services used throughout the API."""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import AccountNotActiveError
from app.repositories.health_repository import HealthRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import User
from app.services.cart_service import CartRepositoryInterface, CartService
from app.services.health_service import HealthService
from app.services.menu_service import MenuService
from app.services.restaurant_service import RestaurantService
from app.services.user_service import UserService

# Tell fastapi to expect an Authentication header
user_token = OAuth2PasswordBearer(tokenUrl="token")

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
    return UserRepository()


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Provide a user service backed by the repository dependency."""
    return UserService(repository=repository)


def get_current_user(token: str = Depends(user_token), repository: UserRepository = Depends(get_user_repository)):
    """Gets the current user from the token"""
    return repository.get_current_user(token)


def get_current_active_customer(current_user: User = Depends(get_current_user)) -> User:
    """Return the signed-in user, or raise AccountNotActiveError (403) if their account is deactivated."""
    if not current_user.account_is_active:
        raise AccountNotActiveError(current_user.reason_for_deactivation or "Unspecified")
    return current_user


def get_cart_repository() -> CartRepositoryInterface:
    """Build the cart repository (#95). Imported here so the app still starts before it exists."""
    # CartRepository arrives with #95; until then this import fails only when the cart is used.
    from app.repositories.cart_repository import CartRepository  # pylint: disable=import-outside-toplevel,no-name-in-module
    return CartRepository()


def get_cart_service(
    repository: CartRepositoryInterface = Depends(get_cart_repository),
    menu_service: MenuService = Depends(get_menu_service),
) -> CartService:
    """Provide a cart service backed by the cart repository and the menu service."""
    return CartService(repository=repository, menu_service=menu_service)
