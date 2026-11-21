"""End-to-end customer flow over HTTP: login -> menu -> cart -> checkout -> order.

Nothing is mocked except where the JSON files live (a temp copy of data/),
so every request runs through the real routes, services, repositories and
id generation.
"""
import pytest

from app.api.deps import get_current_user, get_order_repository
from app.main import app
from app.repositories.order_repository import OrderRepository


@pytest.fixture
#User logs in, browses a restaurant's menu, adds an item to the cart
def api(client, isolated_data_dir):
    app.dependency_overrides[get_order_repository] = lambda: OrderRepository(data_dir=isolated_data_dir)
    app.dependency_overrides.pop(get_current_user, None)  # use real login, not the fake admin
    return client

#Customer order flow: login ->menu -> cart -> checkout -> order -> verify order saved to disk``
def test_customer_can_order_from_a_menu(api, isolated_data_dir):
    # 1. Customer logs in
    login = api.post("/auth/login", json={"username": "UserName2", "password": "superHardPassword1234"})
    assert login.status_code == 200
    auth = {"Authorization": f"Bearer {login.json()}"}

    # 2. Customer browses a restaurant's menu
    menu = api.get("/restaurants/r01/menu")
    assert menu.status_code == 200
    item = menu.json()[0]

    # 3. Customer adds that item to their cart
    cart = api.post("/cart/items", json={"restaurant_id": "r01", "menu_item_id": item["id"], "quantity": 2}, headers=auth)
    assert cart.status_code == 200
    assert api.get("/cart", headers=auth).json()["items"][0]["quantity"] == 2

    # 4. Customer checks out
    checkout = api.post("/cart/checkout", headers=auth)
    assert checkout.status_code == 200
    order = checkout.json()
    assert order["customer_id"] == "c02"
    assert order["total"] == pytest.approx(item["price"] * 2)

    # 5. The order can be fetched back, and it was saved to disk
    assert api.get(f"/orders/{order['id']}", headers=auth).json() == order
    assert OrderRepository(data_dir=isolated_data_dir).get_order(order["id"]) == order
