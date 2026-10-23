from typing import Callable, Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AuthenticationError, PermissionDeniedError

from app.repositories.health_repository import HealthRepository
from app.services.health_service import HealthService

from app.repositories.restaurant_repository import RestaurantRepository
from app.services.restaurant_service import RestaurantService

from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.customer_service import CustomerService

from app.repositories.cart_repository import CartRepository
from app.services.cart_service import CartService

from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService

from app.schemas.user_schema import CurrentUser, UserRole


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


############################################################################################
### Customers + auth
############################################################################################

def get_user_repository() -> UserRepository:
    """Dependency provider for UserRepository."""
    return UserRepository()


def get_auth_service(
    repository: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """Dependency provider for AuthService with injected repository."""
    return AuthService(repository=repository)


def get_customer_service(
    repository: UserRepository = Depends(get_user_repository)
) -> CustomerService:
    """Dependency provider for CustomerService with injected repository."""
    return CustomerService(repository=repository)


############################################################################################
### Cart
############################################################################################

def get_cart_repository() -> CartRepository:
    """Dependency provider for CartRepository."""
    return CartRepository()


def get_cart_service(
    repository: CartRepository = Depends(get_cart_repository),
    restaurant_service: RestaurantService = Depends(get_restaurant_service),
    customer_service: CustomerService = Depends(get_customer_service),
) -> CartService:
    """Dependency provider for CartService with injected repository and collaborating services."""
    return CartService(
        repository=repository,
        restaurant_service=restaurant_service,
        customer_service=customer_service,
    )


############################################################################################
### Orders
############################################################################################

def get_order_repository() -> OrderRepository:
    """Dependency provider for OrderRepository."""
    return OrderRepository()


def get_order_service(
    repository: OrderRepository = Depends(get_order_repository),
    cart_service: CartService = Depends(get_cart_service),
    customer_service: CustomerService = Depends(get_customer_service),
    restaurant_service: RestaurantService = Depends(get_restaurant_service),
) -> OrderService:
    """Dependency provider for OrderService with injected repository and collaborating services."""
    return OrderService(
        repository=repository,
        cart_service=cart_service,
        customer_service=customer_service,
        restaurant_service=restaurant_service,
    )


############################################################################################
### Authentication and authorization
###
### This is the ONE place the backend decides who is calling (get_current_user)
### and whether their role is allowed (require_roles). Routes opt in by depending on them.
############################################################################################

# auto_error=False so a missing header raises our AuthenticationError (401) instead of FastAPI's default
bearer_scheme = HTTPBearer(auto_error=False, description="Token returned by POST /auth/login")


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> CurrentUser:
    """Identify the caller from the 'Authorization: Bearer <token>' header. 401 if missing/invalid."""
    if credentials is None:
        raise AuthenticationError("Missing bearer token. Sign in with POST /auth/login.")
    return auth_service.get_current_user(credentials.credentials)


def require_roles(*allowed_roles: UserRole) -> Callable[..., CurrentUser]:
    """Build a dependency that only lets the given roles through. 403 otherwise.

    Usage: current_user: CurrentUser = Depends(require_roles(UserRole.CUSTOMER))
    """
    def check_role(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise PermissionDeniedError(
                f"This operation requires role: {', '.join(role.value for role in allowed_roles)}."
            )
        return current_user

    return check_role
