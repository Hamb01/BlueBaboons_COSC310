"""Checkout endpoint and orchestration tests."""

from fastapi.testclient import TestClient
import pytest

from app.api.deps import (
    get_cart_repository,
    get_cart_service,
    get_checkout_service,
    get_current_user,
    get_menu_repository,
    get_menu_service,
    get_order_repository,
    get_order_service,
    get_user_repository,
    get_user_service,
)
from app.main import app
from app.repositories.order_repository import OrderRepository
from app.schemas.cart_schema import CartItemAdd
from app.schemas.user_schema import RestaurantAdmin
from app.services.cart_service import CartService
from app.services.checkout_service import CheckoutService
from app.services.order_service import OrderService


ADMIN_USER = RestaurantAdmin(
    id="a01",
    username="admin",
    name="Test Admin",
    email="admin@example.com",
    password="hashed",
    hash_salt="salt",
    account_is_active=True,
    managed_restaurants=["r01", "r02"],
)


def auth_headers(user_repo, user_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {user_repo.generate_web_token(user_id)}"}


@pytest.fixture
def isolated_order_repo(isolated_data_dir) -> OrderRepository:
    return OrderRepository(data_dir=isolated_data_dir)


@pytest.fixture
def isolated_cart_service(isolated_cart_repo, isolated_menu_service) -> CartService:
    return CartService(repository=isolated_cart_repo, menu_service=isolated_menu_service)


@pytest.fixture
def isolated_order_service(isolated_order_repo) -> OrderService:
    return OrderService(repository=isolated_order_repo)


@pytest.fixture
def isolated_checkout_service(
    isolated_user_service,
    isolated_cart_service,
    isolated_menu_service,
    isolated_order_repo,
) -> CheckoutService:
    return CheckoutService(
        user_service=isolated_user_service,
        cart_service=isolated_cart_service,
        menu_service=isolated_menu_service,
        order_repository=isolated_order_repo,
    )


@pytest.fixture
def checkout_client(
    client: TestClient,
    isolated_user_repo,
    isolated_user_service,
    isolated_cart_repo,
    isolated_cart_service,
    isolated_menu_repo,
    isolated_menu_service,
    isolated_order_repo,
    isolated_order_service,
    isolated_checkout_service,
) -> TestClient:
    """Wire all services and repositories to the isolated test data directory."""
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides[get_user_repository] = lambda: isolated_user_repo
    app.dependency_overrides[get_user_service] = lambda: isolated_user_service
    app.dependency_overrides[get_cart_repository] = lambda: isolated_cart_repo
    app.dependency_overrides[get_cart_service] = lambda: isolated_cart_service
    app.dependency_overrides[get_menu_repository] = lambda: isolated_menu_repo
    app.dependency_overrides[get_menu_service] = lambda: isolated_menu_service
    app.dependency_overrides[get_order_repository] = lambda: isolated_order_repo
    app.dependency_overrides[get_order_service] = lambda: isolated_order_service
    app.dependency_overrides[get_checkout_service] = lambda: isolated_checkout_service
    return client


def test_full_checkout_flow_creates_order_and_closes_cart(
    checkout_client: TestClient,
    isolated_user_repo,
    isolated_cart_repo,
    isolated_order_repo,
):
    """Run the Customer -> Menu -> Cart -> Checkout -> Order flow through the API."""
    starting_balance = isolated_user_repo.get_user_data_from_id("c01").balance
    login_response = checkout_client.post(
        "/auth/login",
        json={"username": "UserName1", "password": "HardPassword1234"},
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()}"}

    customer_response = checkout_client.get("/customers/me", headers=headers)
    assert customer_response.status_code == 200
    assert customer_response.json()["username"] == "UserName1"

    menu_response = checkout_client.get("/restaurants/r01/menu")
    assert menu_response.status_code == 200
    item = next(menu_item for menu_item in menu_response.json() if menu_item["id"] == "m01")

    cart_response = checkout_client.post(
        "/cart/items",
        headers=headers,
        json={"restaurant_id": "r01", "menu_item_id": "m01", "quantity": 2},
    )
    assert cart_response.status_code == 200
    assert cart_response.json()["items"][0]["menu_item_id"] == item["id"]

    response = checkout_client.post("/checkout", headers=headers)

    assert response.status_code == 201
    order = response.json()
    expected_total = round(item["price"] * 2, 2)

    assert order["id"] == "o01"
    assert order["customer_id"] == "c01"
    assert order["restaurant_id"] == "r01"
    assert order["status"] == "placed"
    assert order["items"] == [
        {
            "menu_item_id": "m01",
            "name": item["name"],
            "unit_price": item["price"],
            "quantity": 2,
        }
    ]
    assert order["subtotal"] == expected_total
    assert order["total"] == expected_total
    assert isolated_user_repo.get_user_data_from_id("c01").balance == pytest.approx(
        starting_balance - expected_total
    )
    assert isolated_user_repo.store.load()["c01"]["balance"] == pytest.approx(
        starting_balance - expected_total
    )
    order_response = checkout_client.get("/orders/o01", headers=headers)
    assert order_response.status_code == 200
    assert order_response.json() == order
    assert isolated_order_repo.get_order(order["id"]) == order
    assert isolated_cart_repo.get_active_cart("c01") is None


def test_checkout_rejects_mixed_restaurants_and_orders_first_cart(
    checkout_client: TestClient,
    isolated_cart_repo,
    isolated_order_repo,
):
    """Test mixed-restaurant rejection and the address"""
    login_response = checkout_client.post(
        "/auth/login",
        json={"username": "UserName1", "password": "HardPassword1234"},
    )
    assert login_response.status_code == 200
    headers = {"Authorization": f"Bearer {login_response.json()}"}
    customer = checkout_client.get("/customers/me", headers=headers).json()
    menus = [
        checkout_client.get("/restaurants/r01/menu"),
        checkout_client.get("/restaurants/r02/menu"),
    ]
    assert all(menu.status_code == 200 for menu in menus)
    first_item = next(item for item in menus[0].json() if item["id"] == "m01")
    second_item = next(item for item in menus[1].json() if item["id"] == "m01")

    assert checkout_client.post(
        "/cart/items",
        headers=headers,
        json={"restaurant_id": "r01", "menu_item_id": first_item["id"]},
    ).status_code == 200
    rejected_add = checkout_client.post(
        "/cart/items",
        headers=headers,
        json={"restaurant_id": "r02", "menu_item_id": second_item["id"]},
    )
    assert rejected_add.status_code == 409

    cart = checkout_client.get("/cart", headers=headers).json()
    assert cart["restaurant_id"] == "r01"
    assert [line["menu_item_id"] for line in cart["items"]] == [first_item["id"]]

    checkout_response = checkout_client.post("/checkout", headers=headers)
    assert checkout_response.status_code == 201
    order = checkout_response.json()
    assert order["customer_id"] == "c01"
    assert order["restaurant_id"] == "r01"
    assert order["delivery_address"] == customer["address"]
    assert [line["menu_item_id"] for line in order["items"]] == [first_item["id"]]
    assert checkout_client.get(
        f"/orders/{order['id']}", headers=headers
    ).json() == order
    assert isolated_order_repo.get_order(order["id"]) == order
    assert isolated_cart_repo.get_active_cart("c01") is None


def test_checkout_deactivated_customer_returns_403(
    checkout_client: TestClient,
    isolated_user_repo,
    isolated_user_service,
):
    """Deactivated customer is rejected with 403."""
    isolated_user_service.deactivate_customer(
        "c01",
        current_user=isolated_user_repo.get_user_data_from_id("c01"),
        reason_for_deactivation="Policy violation",
    )

    response = checkout_client.post("/checkout", headers=auth_headers(isolated_user_repo, "c01"))

    assert response.status_code == 403


def test_checkout_requires_authentication(checkout_client):
    response = checkout_client.post("/checkout")

    assert response.status_code == 401


def test_checkout_without_an_active_cart_returns_409(
    checkout_client: TestClient,
    isolated_user_repo,
    isolated_cart_repo,
    isolated_order_repo,
):
    response = checkout_client.post(
        "/checkout", headers=auth_headers(isolated_user_repo, "c01")
    )

    assert response.status_code == 409
    assert isolated_cart_repo.get_active_cart("c01") is None
    assert isolated_order_repo.orders == {}


def test_checkout_empty_cart_returns_409(
    checkout_client: TestClient,
    isolated_user_repo,
    isolated_cart_repo,
    isolated_order_repo,
):
    """Checking out with no active cart or an empty cart returns 409."""
    isolated_cart_repo.create_cart("c01")

    response = checkout_client.post("/checkout", headers=auth_headers(isolated_user_repo, "c01"))

    assert response.status_code == 409
    assert isolated_order_repo.orders == {}


def test_checkout_with_insufficient_balance_keeps_cart_and_creates_no_order(
    checkout_client: TestClient,
    isolated_user_repo,
    isolated_cart_repo,
    isolated_cart_service,
    isolated_order_repo,
):
    """Insufficient funds reject checkout without charging or modifying the cart."""
    isolated_user_repo.users["c01"]["balance"] = 1.00
    isolated_user_repo.store.save(isolated_user_repo.users)
    isolated_cart_service.add_item(
        "c01", CartItemAdd(restaurant_id="r01", menu_item_id="m01", quantity=1)
    )
    cart_before = isolated_cart_repo.get_active_cart("c01")

    response = checkout_client.post(
        "/checkout", headers=auth_headers(isolated_user_repo, "c01")
    )

    assert response.status_code == 409
    assert "Insufficient balance" in response.json()["message"]
    assert isolated_user_repo.get_user_data_from_id("c01").balance == 1.00
    assert isolated_cart_repo.get_active_cart("c01") == cart_before
    assert isolated_order_repo.orders == {}


@pytest.mark.parametrize(
    ("menu_change", "remove_item"),
    [
        ({"availability": False}, False),
        ({"is_active": False}, False),
        ({}, True),
    ],
    ids=["unavailable", "inactive", "deleted"],
)
def test_checkout_rejects_unavailable_inactive_or_deleted_items(
    checkout_client: TestClient,
    isolated_user_repo,
    isolated_menu_service,
    isolated_cart_service,
    isolated_cart_repo,
    isolated_order_repo,
    menu_change,
    remove_item,
):
    """Non-orderable or deleted items return 409 without changing cart or orders."""
    isolated_cart_service.add_item(
        "c01", CartItemAdd(restaurant_id="r01", menu_item_id="m01", quantity=1)
    )
    cart_before = isolated_cart_repo.get_active_cart("c01")
    if remove_item:
        isolated_menu_service.remove_menu_item(
            "r01", "m01", current_user=ADMIN_USER
        )
    else:
        isolated_menu_service.update_menu_item(
            "r01", "m01", menu_change, current_user=ADMIN_USER
        )

    response = checkout_client.post("/checkout", headers=auth_headers(isolated_user_repo, "c01"))

    assert response.status_code == 409
    assert isolated_order_repo.orders == {}
    assert isolated_cart_repo.get_active_cart("c01") == cart_before


def test_checkout_recalculates_when_price_changes_before_checkout(
    checkout_client: TestClient,
    isolated_user_repo,
    isolated_menu_service,
    isolated_cart_service,
):
    """Price change after adding to cart is reflected in the placed order."""
    isolated_cart_service.add_item(
        "c01", CartItemAdd(restaurant_id="r01", menu_item_id="m01", quantity=2)
    )
    isolated_menu_service.update_menu_item(
        "r01",
        "m01",
        {"price": 12.50},
        current_user=ADMIN_USER,
    )

    response = checkout_client.post("/checkout", headers=auth_headers(isolated_user_repo, "c01"))

    assert response.status_code == 201
    order = response.json()
    assert order["items"][0]["unit_price"] == 12.50
    assert order["subtotal"] == 25.00
    assert order["total"] == 25.00


def test_checkout_order_save_failure_returns_500_and_leaves_cart_intact(
    checkout_client: TestClient,
    monkeypatch,
    isolated_user_repo,
    isolated_menu_service,
    isolated_cart_service,
    isolated_cart_repo,
    isolated_order_repo,
):
    """Simulated order save failure returns 500, stores no order, and keeps cart active."""
    starting_balance = isolated_user_repo.get_user_data_from_id("c01").balance
    isolated_cart_service.add_item(
        "c01", CartItemAdd(restaurant_id="r01", menu_item_id="m01", quantity=1)
    )
    cart_before = isolated_cart_repo.get_active_cart("c01")

    def boom(_order_data):
        raise OSError("Simulated disk write failure")

    monkeypatch.setattr(isolated_order_repo, "create_order", boom)

    response = checkout_client.post("/checkout", headers=auth_headers(isolated_user_repo, "c01"))

    assert response.status_code == 500
    assert isolated_cart_repo.get_active_cart("c01") == cart_before
    assert getattr(isolated_order_repo, "orders", {}) == {}
    assert isolated_user_repo.get_user_data_from_id("c01").balance == starting_balance