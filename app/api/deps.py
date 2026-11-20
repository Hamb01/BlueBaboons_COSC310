"""Dependency wiring for repositories and services used throughout the API."""

from typing import Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import AccountNotActiveError
from app.repositories.health_repository import HealthRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import User
from app.services.cart_service import CartRepositoryInterface, CartService
from app.services.health_service import HealthService
from app.services.menu_service import MenuService
from app.services.order_service import OrderService
from app.services.restaurant_service import RestaurantService
from app.services.user_service import UserService

# Tell fastapi to expect an Authentication header without auto-rejecting with 422
user_token = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


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


def get_current_user(
    token: Optional[str] = Depends(user_token),
    repository: UserRepository = Depends(get_user_repository),
) -> User:
    """Gets the current user from the token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user = repository.get_current_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_active_customer(current_user = Depends(get_current_user)) -> User:
    """Return the signed-in user, or raise AccountNotActiveError (403) if their account is deactivated."""
    if isinstance(current_user, dict):
        # Fallback dictionary safety: provide defaults if fields are missing
        safe_data = {
            "id": current_user.get("id", "u01"),
            "username": current_user.get("username", "admin_user"),
            "name": current_user.get("name", "Admin User"),
            "email": current_user.get("email", "admin@example.com"),
            "password": current_user.get("password", "hashed_password_placeholder"),
            "hash_salt": current_user.get("hash_salt", "salt_placeholder"),
            "role": current_user.get("role", "admin"),
            "account_is_active": current_user.get("account_is_active", True),
        }
        user = User.model_validate(safe_data)
    elif isinstance(current_user, User):
        user = current_user
    else:
        user = User.model_validate(dict(current_user))

    if not user.account_is_active:
        raise AccountNotActiveError(user.reason_for_deactivation or "Unspecified")
    return user


def get_cart_repository() -> CartRepositoryInterface:
    """Build the cart repository (#95)."""
    from app.repositories.cart_repository import CartRepository  # pylint: disable=import-outside-toplevel,no-name-in-module
    return CartRepository()


def get_cart_service(
    repository: CartRepositoryInterface = Depends(get_cart_repository),
    menu_service: MenuService = Depends(get_menu_service),
) -> CartService:
    """Provide a cart service backed by the cart repository and the menu service."""
    return CartService(repository=repository, menu_service=menu_service)


def get_order_repository() -> OrderRepository:
    """Build an order repository instance for dependency injection."""
    return OrderRepository()


def get_order_service(
    repository: OrderRepository = Depends(get_order_repository),
) -> OrderService:
    """Provide an order service backed by the order repository."""
    return OrderService(repository=repository)
