"""Order tests."""
import pytest

from app.api.deps import get_current_user, get_order_repository
from app.main import app
from app.repositories.order_repository import OrderRepository
from app.schemas.user_schema import RestaurantAdmin


def make_order(customer_id="c01", created_at="2026-11-17T10:00:00+00:00"):
    return {
        "customer_id": customer_id,
        "restaurant_id": "r01",
        "status": "placed",
        "delivery_address": "213-2532 Shoreline Dr, Lake Country, BC",
        "items": [{"menu_item_id": "m01", "name": "Beef Taco", "unit_price": 7.99, "quantity": 2}],
        "subtotal": 15.98,
        "total": 15.98,
        "created_at": created_at,
    }


@pytest.fixture
def order_repo(isolated_data_dir):
    return OrderRepository(data_dir=isolated_data_dir)


@pytest.fixture
def api(client, order_repo):
    app.dependency_overrides[get_order_repository] = lambda: order_repo
    app.dependency_overrides.pop(get_current_user, None)
    return client


def login(user_repo, user_id):
    return {"Authorization": f"Bearer {user_repo.generate_web_token(user_id)}"}


def test_orders_get_ids_and_survive_a_restart(order_repo, isolated_data_dir):
    first = order_repo.create_order(make_order())
    assert first["id"] == "o01"
    assert order_repo.create_order(make_order())["id"] == "o02"

    assert OrderRepository(data_dir=isolated_data_dir).get_order("o01") == first


def test_needs_a_token(api):
    assert api.get("/orders/o01").status_code == 401
    assert api.get("/customers/me/orders").status_code == 401


def test_customer_can_see_their_own_order(api, order_repo, isolated_user_repo):
    created = order_repo.create_order(make_order(customer_id="c01"))

    response = api.get(f"/orders/{created['id']}", headers=login(isolated_user_repo, "c01"))

    assert response.status_code == 200
    assert response.json() == created


def test_customer_cannot_see_someone_elses_order(api, order_repo, isolated_user_repo):
    created = order_repo.create_order(make_order(customer_id="c01"))

    response = api.get(f"/orders/{created['id']}", headers=login(isolated_user_repo, "c02"))

    assert response.status_code == 403


def test_unknown_order_is_404(api, isolated_user_repo):
    assert api.get("/orders/o99", headers=login(isolated_user_repo, "c01")).status_code == 404


def test_my_orders_only_has_mine_newest_first(api, order_repo, isolated_user_repo):
    order_repo.create_order(make_order(created_at="2026-11-01T10:00:00+00:00"))
    order_repo.create_order(make_order(customer_id="c02"))
    order_repo.create_order(make_order(created_at="2026-11-15T10:00:00+00:00"))

    response = api.get("/customers/me/orders", headers=login(isolated_user_repo, "c01"))

    assert [order["id"] for order in response.json()] == ["o03", "o01"]


def test_order_keeps_its_price_after_the_menu_changes(api, order_repo, isolated_user_repo, isolated_menu_service):
    created = order_repo.create_order(make_order(customer_id="c01"))
    isolated_menu_service.update_menu_item(
        "r01",
        "m01",
        {"price": 99.0},
        current_user=RestaurantAdmin(
            id="a01",
            username="admin",
            name="Test Admin",
            email="admin@example.com",
            password="hashed",
            hash_salt="salt",
            account_is_active=True,
            managed_restaurants=["r01", "r02"],
        ),
    )

    order = api.get(f"/orders/{created['id']}", headers=login(isolated_user_repo, "c01")).json()

    assert order["items"][0]["unit_price"] == 7.99
    assert order["total"] == 15.98
