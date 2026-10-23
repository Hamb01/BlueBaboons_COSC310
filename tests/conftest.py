from pathlib import Path
from typing import Callable, Generator, Optional
import pytest
from fastapi.testclient import TestClient
from shutil import copytree

from app.main import app
from app.api.deps import get_health_repository, get_health_service
from app.repositories.health_repository import HealthRepository
from app.services.health_service import HealthService

from app.api.deps import get_restaurant_repository, get_restaurant_service
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.restaurant_service import RestaurantService

from app.api.deps import (
    get_auth_service,
    get_cart_repository,
    get_cart_service,
    get_current_user,
    get_customer_service,
    get_order_repository,
    get_order_service,
    get_user_repository,
)
from app.repositories.user_repository import UserRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.services.auth_service import AuthService
from app.services.customer_service import CustomerService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.schemas.user_schema import CurrentUser, UserRole

# this document contains pytest fixtures,
# fixtures are functions that can be injected into other tests 
# they are just setup code so we don't need to redefine this stuff for every indivdual test

############################################################################################
### General Config for all tests
###
### These make sure that all our tests get to use versions of the actual data and methods
### that make up our app without actually interfering with our saved date 
############################################################################################

@pytest.fixture
def isolated_data_dir(empty_isolated_data_dir: Path) -> Path:
    """Provides an isolated directory representing the persistence layer."""

    return populate_test_data(empty_isolated_data_dir)

@pytest.fixture
def empty_isolated_data_dir(tmp_path: Path) -> Path:
    """Provides an isolated directory representing the persistance layer for functions that do not need to read the existing files"""

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

@pytest.fixture
def client(
    isolated_health_service: HealthService,
    isolated_health_repo: HealthRepository,
    isolated_restaurant_service: RestaurantService,
    isolated_restaurant_repo: RestaurantRepository,
    isolated_user_repo: UserRepository,
    isolated_auth_service: AuthService,
    isolated_customer_service: CustomerService,
    isolated_cart_repo: CartRepository,
    isolated_cart_service: CartService,
    isolated_order_repo: OrderRepository,
    isolated_order_service: OrderService,
) -> Generator[TestClient, None, None]:
    """FastAPI TestClient fixture with dependency overrides for isolated testing."""

    app.dependency_overrides[get_health_repository] = lambda: isolated_health_repo
    app.dependency_overrides[get_health_service]    = lambda: isolated_health_service
    app.dependency_overrides[get_restaurant_repository] = lambda: isolated_restaurant_repo
    app.dependency_overrides[get_restaurant_service]    = lambda: isolated_restaurant_service
    app.dependency_overrides[get_user_repository]   = lambda: isolated_user_repo
    app.dependency_overrides[get_auth_service]      = lambda: isolated_auth_service
    app.dependency_overrides[get_customer_service]  = lambda: isolated_customer_service
    app.dependency_overrides[get_cart_repository]   = lambda: isolated_cart_repo
    app.dependency_overrides[get_cart_service]      = lambda: isolated_cart_service
    app.dependency_overrides[get_order_repository]  = lambda: isolated_order_repo
    app.dependency_overrides[get_order_service]     = lambda: isolated_order_service

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()

def populate_test_data(temp_data_dir: Path):
    """Copy Restaurant Data into Isolated Testing Directory"""

    seed_data_dir = Path(__file__).resolve().parents[1] / "data"
    copytree(seed_data_dir, temp_data_dir, dirs_exist_ok=True)
    return temp_data_dir


############################################################################################
### Config for test_health.py
############################################################################################

@pytest.fixture
def isolated_health_repo(isolated_data_dir: Path) -> HealthRepository:
    return HealthRepository(data_dir = isolated_data_dir)


@pytest.fixture
def isolated_health_service(isolated_health_repo: HealthRepository) -> HealthService:
    return HealthService(repository = isolated_health_repo)


############################################################################################
### Config for restaurants.py
############################################################################################

@pytest.fixture
def isolated_restaurant_repo(isolated_data_dir: Path) -> RestaurantRepository:
    return RestaurantRepository(data_dir = isolated_data_dir)

@pytest.fixture
def isolated_restaurant_service(isolated_restaurant_repo: RestaurantRepository) -> RestaurantService:
    return RestaurantService(repository = isolated_restaurant_repo)


############################################################################################
### Config for customers + auth (Person A)
############################################################################################

@pytest.fixture
def isolated_user_repo(isolated_data_dir: Path) -> UserRepository:
    return UserRepository(data_dir = isolated_data_dir)

@pytest.fixture
def isolated_auth_service(isolated_user_repo: UserRepository) -> AuthService:
    return AuthService(repository = isolated_user_repo)

@pytest.fixture
def isolated_customer_service(isolated_user_repo: UserRepository) -> CustomerService:
    return CustomerService(repository = isolated_user_repo)


@pytest.fixture
def login_as() -> Callable[..., CurrentUser]:
    """Skip real sign-in in API tests by overriding get_current_user.

    Usage (inside a test that also uses `client`):
        login_as()                                  # customer u01
        login_as("u02")                             # customer u02
        login_as("u05", role=UserRole.ADMIN)        # admin
    Lets cart/order tests run before the real token logic exists.
    Tests of authentication itself should NOT use this; they should call /auth/login.
    """
    def _login_as(
        user_id: str = "u01",
        role: UserRole = UserRole.CUSTOMER,
        restaurant_id: Optional[str] = None,
    ) -> CurrentUser:
        # TODO: update this call once CurrentUser has its fields (it ignores unknown fields until then)
        user = CurrentUser(id = user_id, role = role, restaurant_id = restaurant_id)
        app.dependency_overrides[get_current_user] = lambda: user
        return user

    return _login_as


############################################################################################
### Config for cart (Person B)
############################################################################################

@pytest.fixture
def isolated_cart_repo(isolated_data_dir: Path) -> CartRepository:
    return CartRepository(data_dir = isolated_data_dir)

@pytest.fixture
def isolated_cart_service(
    isolated_cart_repo: CartRepository,
    isolated_restaurant_service: RestaurantService,
    isolated_customer_service: CustomerService,
) -> CartService:
    return CartService(
        repository = isolated_cart_repo,
        restaurant_service = isolated_restaurant_service,
        customer_service = isolated_customer_service,
    )


############################################################################################
### Config for checkout + orders (Person C)
############################################################################################

@pytest.fixture
def isolated_order_repo(isolated_data_dir: Path) -> OrderRepository:
    return OrderRepository(data_dir = isolated_data_dir)

@pytest.fixture
def isolated_order_service(
    isolated_order_repo: OrderRepository,
    isolated_cart_service: CartService,
    isolated_customer_service: CustomerService,
    isolated_restaurant_service: RestaurantService,
) -> OrderService:
    return OrderService(
        repository = isolated_order_repo,
        cart_service = isolated_cart_service,
        customer_service = isolated_customer_service,
        restaurant_service = isolated_restaurant_service,
    )
