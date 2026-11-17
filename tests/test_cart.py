"""Tests for the cart service and cart API (issues #95 get cart, #96 add items).

The cart repository is being built separately (#95). InMemoryCartRepository below
implements the same interface (CartRepositoryInterface in cart_service.py), so the
service and routes can be tested now and the real repository can be dropped in later.
"""
from typing import Any, Dict, Optional
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_cart_repository
from app.core.exceptions import (
    CartRestaurantConflictError,
    MenuItemNotFoundError,
    MenuItemUnavailableError,
)
from app.main import app
from app.repositories.user_repository import UserRepository
from app.schemas.cart_schema import CartItemAdd
from app.schemas.menu_item import MenuItem
from app.services.cart_service import CartService
from app.services.menu_service import MenuService


class InMemoryCartRepository:
    """Test double that follows CartRepositoryInterface without touching any file."""

    def __init__(self):
        self.carts: Dict[str, Dict[str, Any]] = {}
        self.saves = 0

    def get_active_cart(self, customer_id: str) -> Optional[Dict[str, Any]]:
        for cart in self.carts.values():
            if cart["customer_id"] == customer_id and cart["status"] == "active":
                return dict(cart)
        return None

    def create_cart(self, customer_id: str) -> Dict[str, Any]:
        cart = {"id": f"k{len(self.carts) + 1:02d}", "customer_id": customer_id,
                "restaurant_id": None, "items": [], "status": "active"}
        self.carts[cart["id"]] = cart
        return dict(cart)

    def save_cart(self, cart: Dict[str, Any]) -> Dict[str, Any]:
        self.carts[cart["id"]] = dict(cart)
        self.saves += 1
        return dict(cart)


TACO = MenuItem(id="m01", restaurant_id="r01", name="Beef Taco",
                description="Beef tacos", price=7.99, availability=True)
SOLD_OUT = MenuItem(id="m02", restaurant_id="r01", name="Fish Taco",
                    description="Sold out", price=9.0, availability=False)
SUSHI = MenuItem(id="m01", restaurant_id="r02", name="California Rolls",
                 description="8 rolls", price=12.99, availability=True)


@pytest.fixture
def cart_repo():
    return InMemoryCartRepository()


@pytest.fixture
def menu():
    """A MenuService stand-in that knows three items."""
    items = {("r01", "m01"): TACO, ("r01", "m02"): SOLD_OUT, ("r02", "m01"): SUSHI}
    mock = Mock(spec=MenuService)

    def get_menu_item(restaurant_id, item_id):
        if (restaurant_id, item_id) not in items:
            raise MenuItemNotFoundError(restaurant_id, item_id)
        return items[(restaurant_id, item_id)]

    mock.get_menu_item.side_effect = get_menu_item
    return mock


@pytest.fixture
def service(cart_repo, menu):
    return CartService(repository=cart_repo, menu_service=menu)


############################################################################################
### Service: get or create the active cart (#95)
############################################################################################

def test_first_request_creates_an_empty_cart_and_later_requests_reuse_it(service, cart_repo):
    first = service.get_active_cart("c01")
    second = service.get_active_cart("c01")

    assert first.id == second.id == "k01"
    assert first.items == [] and first.subtotal == 0 and first.restaurant_id is None
    assert len(cart_repo.carts) == 1


def test_each_customer_gets_their_own_cart(service):
    assert service.get_active_cart("c01").id != service.get_active_cart("c02").id


############################################################################################
### Service: add items (#96)
############################################################################################

def test_add_item_creates_a_line_and_prices_it(service):
    cart = service.add_item("c01", CartItemAdd(restaurant_id="r01", menu_item_id="m01", quantity=2))

    assert cart.restaurant_id == "r01"
    assert [(line.menu_item_id, line.quantity, line.unit_price, line.line_total) for line in cart.items] == [
        ("m01", 2, 7.99, 15.98)]
    assert cart.subtotal == cart.total == 15.98


def test_adding_the_same_item_again_increases_quantity_instead_of_duplicating(service):
    service.add_item("c01", CartItemAdd(restaurant_id="r01", menu_item_id="m01", quantity=1))
    cart = service.add_item("c01", CartItemAdd(restaurant_id="r01", menu_item_id="m01", quantity=2))

    assert len(cart.items) == 1
    assert cart.items[0].quantity == 3
    assert cart.total == 23.97


def test_unavailable_item_is_rejected_and_nothing_is_saved(service, cart_repo):
    with pytest.raises(MenuItemUnavailableError):
        service.add_item("c01", CartItemAdd(restaurant_id="r01", menu_item_id="m02"))

    assert cart_repo.saves == 0


def test_unknown_item_is_rejected_and_nothing_is_saved(service, cart_repo):
    with pytest.raises(MenuItemNotFoundError):
        service.add_item("c01", CartItemAdd(restaurant_id="r01", menu_item_id="m99"))

    assert cart_repo.saves == 0


def test_items_from_a_second_restaurant_are_rejected_and_cart_is_unchanged(service, cart_repo):
    service.add_item("c01", CartItemAdd(restaurant_id="r01", menu_item_id="m01"))
    before = cart_repo.get_active_cart("c01")

    with pytest.raises(CartRestaurantConflictError):
        service.add_item("c01", CartItemAdd(restaurant_id="r02", menu_item_id="m01"))

    assert cart_repo.get_active_cart("c01") == before
    assert cart_repo.saves == 1


def test_totals_always_use_the_current_menu_price(service, menu):
    service.add_item("c01", CartItemAdd(restaurant_id="r01", menu_item_id="m01", quantity=2))
    cheaper = TACO.model_copy(update={"price": 5.0})
    menu.get_menu_item.side_effect = lambda restaurant_id, item_id: cheaper

    cart = service.get_active_cart("c01")

    assert cart.items[0].unit_price == 5.0
    assert cart.total == 10.0


def test_item_removed_from_the_menu_stays_visible_but_is_not_charged(service, menu):
    service.add_item("c01", CartItemAdd(restaurant_id="r01", menu_item_id="m01"))
    menu.get_menu_item.side_effect = MenuItemNotFoundError("r01", "m01")

    cart = service.get_active_cart("c01")

    assert cart.items[0].available is False
    assert cart.total == 0


############################################################################################
### API: authentication and HTTP status codes (real menu data, real JWT)
############################################################################################

@pytest.fixture
def cart_client(client: TestClient, cart_repo):
    """The app client with the cart repository replaced by the in-memory one."""
    app.dependency_overrides[get_cart_repository] = lambda: cart_repo
    return client


@pytest.fixture
def auth(isolated_user_repo: UserRepository):
    """Authorization header for seed customer c01."""
    return {"Authorization": f"Bearer {isolated_user_repo.generate_web_token('c01')}"}


def test_cart_requires_a_token(cart_client):
    assert cart_client.get("/cart").status_code == 401
    assert cart_client.post("/cart/items", json={"restaurant_id": "r01", "menu_item_id": "m01"}).status_code == 401


def test_get_cart_returns_the_same_empty_cart_twice(cart_client, auth):
    first = cart_client.get("/cart", headers=auth)
    second = cart_client.get("/cart", headers=auth)

    assert first.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["items"] == []


def test_add_item_returns_cart_with_backend_totals(cart_client, auth):
    response = cart_client.post("/cart/items", headers=auth,
                                json={"restaurant_id": "r01", "menu_item_id": "m01", "quantity": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["name"] == "Beef Taco"
    assert body["subtotal"] == body["total"] == 15.98


@pytest.mark.parametrize("quantity", [0, -1])
def test_quantity_below_one_returns_422(cart_client, auth, quantity):
    response = cart_client.post("/cart/items", headers=auth,
                                json={"restaurant_id": "r01", "menu_item_id": "m01", "quantity": quantity})
    assert response.status_code == 422


def test_unknown_item_returns_404(cart_client, auth):
    response = cart_client.post("/cart/items", headers=auth, json={"restaurant_id": "r01", "menu_item_id": "m99"})
    assert response.status_code == 404


def test_unavailable_item_returns_409(cart_client, auth):
    response = cart_client.post("/cart/items", headers=auth, json={"restaurant_id": "r02", "menu_item_id": "m03"})
    assert response.status_code == 409


def test_mixing_restaurants_returns_409(cart_client, auth):
    cart_client.post("/cart/items", headers=auth, json={"restaurant_id": "r01", "menu_item_id": "m01"})
    response = cart_client.post("/cart/items", headers=auth, json={"restaurant_id": "r02", "menu_item_id": "m01"})

    assert response.status_code == 409
    assert response.json()["message"] == "A cart can only contain items from one restaurant."


def test_deactivated_customer_gets_403_and_no_cart_change(cart_client, auth, isolated_user_repo, cart_repo):
    isolated_user_repo.users["c01"]["account_is_active"] = False

    response = cart_client.post("/cart/items", headers=auth, json={"restaurant_id": "r01", "menu_item_id": "m01"})

    assert response.status_code == 403
    assert cart_repo.saves == 0
