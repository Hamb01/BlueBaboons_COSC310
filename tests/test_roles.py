"""Role enforcement with the seeded demo accounts (#89), signing in for real."""
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_restaurant_repository, get_user_repository
from app.main import app
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository

SEED_DATA = Path(__file__).resolve().parents[1] / "data"
LOGINS = {"o01": ("owner1", "owner1pass"), "o02": ("owner2", "owner2pass"), "a01": ("admin1", "admin1pass")}


@pytest.fixture
def role_client(tmp_path):
    """A client on a copy of the committed seed data, with real sign-in (no user override)."""
    data_dir = tmp_path / "data"
    shutil.copytree(SEED_DATA, data_dir)
    app.dependency_overrides[get_restaurant_repository] = lambda: RestaurantRepository(data_dir=data_dir)
    app.dependency_overrides[get_user_repository] = lambda: UserRepository(data_dir=data_dir)
    yield TestClient(app)
    app.dependency_overrides.clear()


def sign_in(client, user_id):
    username, password = LOGINS[user_id]
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()}"}


def test_seed_restaurants_belong_to_seed_owners(role_client):
    assert role_client.get("/restaurants/r01").json()["owner_id"] == "o01"
    assert role_client.get("/restaurants/r02").json()["owner_id"] == "o02"


def test_owner_can_edit_own_restaurant_and_menu(role_client):
    auth = sign_in(role_client, "o01")
    assert role_client.put("/restaurants/r01", headers=auth, json={"name": "Tacos"}).status_code == 200
    assert role_client.patch("/restaurants/r01/menu/m01", headers=auth, json={"price": 9.99}).status_code == 200


@pytest.mark.parametrize(
    ("changes", "availability", "is_active"),
    [
        ({"availability": False}, False, True),
        ({"is_active": False}, True, False),
    ],
)
def test_owner_can_set_menu_item_order_state(
    role_client, changes, availability, is_active
):
    auth = sign_in(role_client, "o01")

    response = role_client.patch(
        "/restaurants/r01/menu/m01", headers=auth, json=changes
    )

    assert response.status_code == 200
    item = response.json()
    assert item["id"] == "m01"
    assert item["availability"] is availability
    assert item["is_active"] is is_active


def test_owner_cannot_edit_another_owners_restaurant_or_menu(role_client):
    auth = sign_in(role_client, "o01")
    before = role_client.get("/restaurants/r02").json()

    assert role_client.put("/restaurants/r02", headers=auth, json={"name": "Mine now"}).status_code == 403
    assert role_client.patch("/restaurants/r02/menu/m01", headers=auth, json={"price": 0.5}).status_code == 403
    assert role_client.get("/restaurants/r02").json() == before


def test_admin_can_edit_any_restaurant(role_client):
    auth = sign_in(role_client, "a01")
    assert role_client.put("/restaurants/r02", headers=auth, json={"name": "Sushi"}).status_code == 200
