from typing import Callable

from fastapi import Depends

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
### Authentication and authorization (Owner: Person A)
###
### Routes depend on these two functions, so their NAMES and how routes use them are fixed;
### their implementation is yours to design.
############################################################################################

def get_current_user() -> CurrentUser:
    """Identify who is calling this request."""
    # TODO: where does the client put its credentials on each request? (look up fastapi.security)
    # TODO: what should the response be when they are missing vs. invalid?
    # TODO: this is a dependency — it can itself depend on get_auth_service.
    raise NotImplementedError("get_current_user")


def require_roles(*allowed_roles: UserRole) -> Callable[..., CurrentUser]:
    """Build a dependency that only lets the given roles through.

    Usage in a route: current_user: CurrentUser = Depends(require_roles(UserRole.CUSTOMER))
    """
    def check_role(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        # TODO: what should happen when the role is not allowed? How is that different from not signed in?
        raise NotImplementedError("require_roles")

    return check_role
