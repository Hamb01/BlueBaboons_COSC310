"""Tests for CartRepository (#95): stable ids, one active cart, persistence, and the real API."""
from unittest.mock import patch

import pytest

from app.api.deps import get_cart_repository, get_current_user, get_user_repository
from app.core.exceptions import DataPersistenceError
from app.main import app
from app.repositories.cart_repository import CartRepository


@pytest.fixture
def cart_repo(isolated_data_dir):
    return CartRepository(data_dir=isolated_data_dir)


def test_customer_without_a_cart_gets_none(cart_repo):
    assert cart_repo.get_active_cart("c01") is None


def test_create_cart_gives_sequential_ids_and_an_empty_cart(cart_repo):
    first = cart_repo.create_cart("c01")

    assert first == {"id": "k01", "customer_id": "c01", "restaurant_id": None, "items": [], "status": "active"}
    assert cart_repo.create_cart("c02")["id"] == "k02"
    assert cart_repo.get_active_cart("c01") == first


def test_carts_survive_a_restart(cart_repo, isolated_data_dir):
    cart = cart_repo.create_cart("c01")
    cart["items"] = [{"restaurant_id": "r01", "menu_item_id": "m01", "quantity": 2}]
    cart["restaurant_id"] = "r01"
    cart_repo.save_cart(cart)

    # making a brand new repository is the same as restarting the app
    reloaded = CartRepository(data_dir=isolated_data_dir)

    assert reloaded.get_active_cart("c01") == cart


def test_failed_save_changes_nothing(cart_repo):
    cart = cart_repo.create_cart("c01")
    with patch.object(cart_repo.store, "save", side_effect=DataPersistenceError("disk full")):
        with pytest.raises(DataPersistenceError):
            cart_repo.save_cart({**cart, "restaurant_id": "r01"})

    assert cart_repo.get_active_cart("c01")["restaurant_id"] is None


def test_cart_api_works_end_to_end_with_the_real_repository(client, cart_repo, isolated_user_repo):
    app.dependency_overrides[get_cart_repository] = lambda: cart_repo
    app.dependency_overrides[get_user_repository] = lambda: isolated_user_repo
    app.dependency_overrides.pop(get_current_user, None)
    
    isolated_user_repo.users["c01"] = {
        "id": "c01",
        "username": "customer01",
        "name": "Customer One",
        "email": "c01@example.com",
        "password": "hashed_password_placeholder",
        "hash_salt": "salt_placeholder",
        "account_is_active": True,
        "address": "1 Main St",
        "city": "Kelowna",
        "province": "BC",
        "postal_code": "V1W 1A1",
        "balance": 0,
    }
    isolated_user_repo.save_to_file()
    
    headers = {"Authorization": f"Bearer {isolated_user_repo.generate_web_token('c01')}"}

    added = client.post("/cart/items", headers=headers,
                        json={"restaurant_id": "r01", "menu_item_id": "m01", "quantity": 2})
    fetched = client.get("/cart", headers=headers)

    assert added.status_code == 200
    assert fetched.status_code == 200
    assert fetched.json()["id"] == added.json()["id"] == "k01"
    assert fetched.json()["total"] == 15.98