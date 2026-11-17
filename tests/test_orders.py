"""Tests for viewing orders (#99 view an order, #100 order history).

Orders are created by checkout (#101). Until that exists, these tests create orders
directly through OrderRepository.create_order, which is the method checkout will call.
"""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_order_repository
from app.core.exceptions import DataPersistenceError, OrderNotFoundError, UserNotAuthorizedError
from app.main import app
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import Customer, Developer, RestaurantOwner
from app.services.order_service import OrderService


def make_order(customer_id="c01", restaurant_id="r01", created_at="2026-11-17T10:00:00+00:00"):
    """Order data as checkout will build it (no id yet)."""
    return {
        "customer_id": customer_id,
        "restaurant_id": restaurant_id,
        "status": "placed",
        "delivery_address": "213-2532 Shoreline Dr, Lake Country, BC V1V 1V6",
        "items": [{"menu_item_id": "m01", "name": "Beef Taco", "unit_price": 7.99,
                   "quantity": 2, "line_total": 15.98}],
        "subtotal": 15.98,
        "total": 15.98,
        "created_at": created_at,
    }


ACCOUNT = {"username": "user", "name": "Test User", "email": "t@example.com",
           "password": "hash", "hash_salt": "salt", "account_is_active": True}


def customer(user_id):
    return Customer(id=user_id, address="1 Main St", city="Kelowna", province="BC",
                    postal_code="V1V 1V7", balance=0, **ACCOUNT)


@pytest.fixture
def order_repo(isolated_data_dir):
    return OrderRepository(data_dir=isolated_data_dir)


@pytest.fixture
def order_service(order_repo):
    return OrderService(repository=order_repo)


############################################################################################
### Repository: stable ids, persistence, safe writes
############################################################################################

def test_new_orders_get_sequential_ids(order_repo):
    assert order_repo.create_order(make_order())["id"] == "o01"
    assert order_repo.create_order(make_order())["id"] == "o02"


def test_orders_survive_a_restart(order_repo, isolated_data_dir):
    created = order_repo.create_order(make_order())

    reloaded = OrderRepository(data_dir=isolated_data_dir)    # a fresh repository = app restart

    assert reloaded.get_order(created["id"]) == created
    assert reloaded.create_order(make_order())["id"] == "o02"


def test_unknown_order_raises_not_found(order_repo):
    with pytest.raises(OrderNotFoundError):
        order_repo.get_order("o99")


def test_failed_save_stores_nothing(order_repo):
    with patch.object(order_repo.store, "save", side_effect=DataPersistenceError("disk full")):
        with pytest.raises(DataPersistenceError):
            order_repo.create_order(make_order())

    assert not order_repo.orders
    with pytest.raises(OrderNotFoundError):
        order_repo.get_order("o01")


############################################################################################
### Service: who may see an order
############################################################################################

def test_customer_can_view_their_own_order(order_repo, order_service):
    created = order_repo.create_order(make_order(customer_id="c01"))

    order = order_service.get_order(created["id"], customer("c01"))

    assert order.items[0].name == "Beef Taco"
    assert order.total == 15.98


def test_customer_cannot_view_someone_elses_order(order_repo, order_service):
    created = order_repo.create_order(make_order(customer_id="c01"))

    with pytest.raises(UserNotAuthorizedError):
        order_service.get_order(created["id"], customer("c02"))


def test_developer_can_view_any_order(order_repo, order_service):
    created = order_repo.create_order(make_order(customer_id="c01"))

    assert order_service.get_order(created["id"], Developer(id="d01", **ACCOUNT)).id == created["id"]


@pytest.mark.parametrize("owned, allowed", [(["r01"], True), (["r02"], False)])
def test_restaurant_owner_sees_only_orders_for_their_restaurants(order_repo, order_service, owned, allowed):
    created = order_repo.create_order(make_order(restaurant_id="r01"))
    owner = RestaurantOwner(id="o01", owned_restaurants=owned, **ACCOUNT)

    if allowed:
        assert order_service.get_order(created["id"], owner).restaurant_id == "r01"
    else:
        with pytest.raises(UserNotAuthorizedError):
            order_service.get_order(created["id"], owner)


def test_order_history_is_newest_first_and_only_mine(order_repo, order_service):
    order_repo.create_order(make_order(created_at="2026-11-01T10:00:00+00:00"))
    order_repo.create_order(make_order(customer_id="c02"))
    order_repo.create_order(make_order(created_at="2026-11-15T10:00:00+00:00"))

    history = order_service.list_my_orders(customer("c01"))

    assert [order.id for order in history] == ["o03", "o01"]


def test_order_history_is_empty_for_a_new_customer(order_service):
    assert not order_service.list_my_orders(customer("c09"))


############################################################################################
### API: authentication, status codes and the price snapshot
############################################################################################

@pytest.fixture
def order_client(client: TestClient, order_repo):
    app.dependency_overrides[get_order_repository] = lambda: order_repo
    return client


def token_for(user_repo: UserRepository, user_id: str) -> dict:
    return {"Authorization": f"Bearer {user_repo.generate_web_token(user_id)}"}


def test_orders_require_a_token(order_client):
    assert order_client.get("/orders/o01").status_code == 401
    assert order_client.get("/customers/me/orders").status_code == 401


def test_get_my_order_returns_200(order_client, order_repo, isolated_user_repo):
    created = order_repo.create_order(make_order(customer_id="c01"))

    response = order_client.get(f"/orders/{created['id']}", headers=token_for(isolated_user_repo, "c01"))

    assert response.status_code == 200
    assert response.json() == created


def test_get_another_customers_order_returns_403(order_client, order_repo, isolated_user_repo):
    created = order_repo.create_order(make_order(customer_id="c01"))

    response = order_client.get(f"/orders/{created['id']}", headers=token_for(isolated_user_repo, "c02"))

    assert response.status_code == 403


def test_unknown_order_returns_404(order_client, isolated_user_repo):
    response = order_client.get("/orders/o99", headers=token_for(isolated_user_repo, "c01"))

    assert response.status_code == 404


def test_my_orders_lists_only_my_orders(order_client, order_repo, isolated_user_repo):
    order_repo.create_order(make_order(customer_id="c01"))
    order_repo.create_order(make_order(customer_id="c02"))

    mine = order_client.get("/customers/me/orders", headers=token_for(isolated_user_repo, "c01"))

    assert mine.status_code == 200
    assert [order["customer_id"] for order in mine.json()] == ["c01"]


def test_deactivated_customer_cannot_read_orders(order_client, order_repo, isolated_user_repo):
    created = order_repo.create_order(make_order(customer_id="c01"))
    isolated_user_repo.users["c01"]["account_is_active"] = False

    response = order_client.get(f"/orders/{created['id']}", headers=token_for(isolated_user_repo, "c01"))

    assert response.status_code == 403


def test_order_keeps_its_price_after_the_menu_price_changes(order_client, order_repo, isolated_user_repo,
                                                            isolated_menu_service):
    created = order_repo.create_order(make_order(customer_id="c01"))
    isolated_menu_service.update_menu_item("r01", "m01", {"price": 99.0})

    order = order_client.get(f"/orders/{created['id']}", headers=token_for(isolated_user_repo, "c01")).json()

    assert isolated_menu_service.get_menu_item("r01", "m01").price == 99.0
    assert order["items"][0]["unit_price"] == 7.99
    assert order["total"] == 15.98
