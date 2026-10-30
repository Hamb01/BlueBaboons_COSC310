"""Regression tests for menu write operations (issues #61, #62, #63)."""
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.exceptions import EmptyMenuError, MenuItemNotFoundError, RestaurantNotFoundError
from app.core.exceptions import MenuItemNotFoundError, RestaurantNotFoundError
from app.repositories.menu_repository import MenuRepository
from app.repositories.restaurant_repository import RestaurantRepository

COMMITTED_DATA = Path(__file__).resolve().parents[1] / "data" / "Restaurants.json"


def reload_menu(data_dir: Path, restaurant_id: str) -> list:
    """Read a menu through a brand-new repository, as if the app had restarted."""
    return MenuRepository(RestaurantRepository(data_dir=data_dir)).get_menu_data(restaurant_id)


def menu_ids(menu: list) -> list:
    return [item["id"] for item in menu]


############################################################################################
### #61 Update a menu item (PUT / PATCH)
############################################################################################

def test_repository_update_changes_only_that_item(isolated_menu_repo, isolated_data_dir):
    before = reload_menu(isolated_data_dir, "r01")
    original = next(item for item in before if item["id"] == "m01")

    updated = isolated_menu_repo.update_menu_item("r01", "m01", {**original, "price": 9.5})

    assert updated["price"] == 9.5
    after = reload_menu(isolated_data_dir, "r01")
    assert menu_ids(after) == menu_ids(before)
    assert next(item for item in after if item["id"] == "m01") == {**original, "price": 9.5}
    assert next(item for item in after if item["id"] == "m02") == next(
        item for item in before if item["id"] == "m02")


def test_updating_twice_does_not_duplicate_items(isolated_menu_service, isolated_data_dir):
    isolated_menu_service.update_menu_item("r01", "m01", {"price": 8.0})
    isolated_menu_service.update_menu_item("r01", "m01", {"price": 8.5})

    after = reload_menu(isolated_data_dir, "r01")
    assert menu_ids(after).count("m01") == 1
    assert next(item for item in after if item["id"] == "m01")["price"] == 8.5


@pytest.mark.parametrize("changes", [{"price": 3.25}, {"availability": False}, {"name": "Fish Taco"}])
def test_partial_update_keeps_other_fields(isolated_menu_service, changes):
    before = isolated_menu_service.get_menu_item("r01", "m01").model_dump()

    updated = isolated_menu_service.update_menu_item("r01", "m01", changes)

    assert updated == {**before, **changes}


def test_update_cannot_change_item_or_restaurant_id(isolated_menu_service):
    updated = isolated_menu_service.update_menu_item(
        "r01", "m01", {"id": "m99", "restaurant_id": "r02", "price": 4.0})

    assert updated["id"] == "m01"
    assert updated["restaurant_id"] == "r01"


def test_invalid_update_is_rejected_before_writing(isolated_menu_service, isolated_restaurant_repo):
    before = isolated_restaurant_repo.master_file.read_bytes()

    with pytest.raises(ValidationError):
        isolated_menu_service.update_menu_item("r01", "m01", {"price": -1})

    assert isolated_restaurant_repo.master_file.read_bytes() == before


def test_update_unknown_item_or_restaurant_raises_domain_errors(isolated_menu_service, isolated_menu_repo):
    with pytest.raises(MenuItemNotFoundError):
        isolated_menu_service.update_menu_item("r01", "m99", {"price": 1})
    with pytest.raises(MenuItemNotFoundError):
        isolated_menu_repo.update_menu_item("r01", "m99", {"price": 1})
    with pytest.raises(RestaurantNotFoundError):
        isolated_menu_service.update_menu_item("unknown", "m01", {"price": 1})


def test_update_on_restaurant_without_menu_key_is_not_a_crash(client, isolated_menu_service):
    created = client.post("/restaurants", json={
        "name": "New Place", "location": "Kelowna", "isOpen": True,
        "cuisine": "Thai", "opening_hours": "10:00-20:00"}).json()

    with pytest.raises((MenuItemNotFoundError, EmptyMenuError)):
    with pytest.raises(MenuItemNotFoundError):
        isolated_menu_service.update_menu_item(created["id"], "m01", {"price": 1})


@pytest.mark.parametrize("method", ["put", "patch"])
def test_update_route_unknown_restaurant_returns_404_not_500(client, method):
    # Path restaurant_id is still typed int until issue #60 lands, so use a numeric id.
    response = getattr(client, method)("/restaurant/1/menu/m01", json={"price": 1})
    assert response.status_code == 404


############################################################################################
### #62 Add a menu item (POST)
############################################################################################

NEW_ITEM = {"restaurant_id": 0, "name": "Fish Taco", "price": 8.25,
            "description": "Battered fish with slaw", "availability": True}


def test_add_menu_item_returns_201_with_new_id(client):
    response = client.post("/restaurant/r01/menu", json=NEW_ITEM)

    assert response.status_code == 201
    item = response.json()["item"]
    assert item["id"] == "m06"
    assert item["restaurant_id"] == "r01"
    assert item["name"] == "Fish Taco"
    assert item["price"] == 8.25
    assert item["availability"] is True


def test_added_item_is_listed_and_persisted(client, isolated_data_dir):
    client.post("/restaurant/r01/menu", json=NEW_ITEM)

    listed = client.get("/restaurants/r01/menu").json()
    assert [item["name"] for item in listed].count("Fish Taco") == 1
    assert "m06" in menu_ids(reload_menu(isolated_data_dir, "r01"))


@pytest.mark.parametrize("availability", [True, False])
def test_add_menu_item_keeps_client_availability(client, availability):
    response = client.post("/restaurant/r01/menu", json={**NEW_ITEM, "availability": availability})
    assert response.json()["item"]["availability"] is availability


def test_add_menu_item_defaults_to_available(client):
    payload = {key: value for key, value in NEW_ITEM.items() if key != "availability"}
    assert client.post("/restaurant/r01/menu", json=payload).json()["item"]["availability"] is True


def test_add_menu_item_rejects_negative_price(client, isolated_restaurant_repo):
    before = isolated_restaurant_repo.master_file.read_bytes()

    response = client.post("/restaurant/r01/menu", json={**NEW_ITEM, "price": -1})

    assert response.status_code == 422
    assert isolated_restaurant_repo.master_file.read_bytes() == before


def test_add_menu_item_unknown_restaurant_returns_404(client):
    assert client.post("/restaurant/unknown/menu", json=NEW_ITEM).status_code == 404


def test_add_menu_item_to_new_restaurant_without_menu_key(client):
    created = client.post("/restaurants", json={
        "name": "New Place", "location": "Kelowna", "isOpen": True,
        "cuisine": "Thai", "opening_hours": "10:00-20:00"}).json()

    response = client.post(f"/restaurant/{created['id']}/menu", json=NEW_ITEM)

    assert response.status_code == 201
    assert menu_ids(client.get(f"/restaurants/{created['id']}/menu").json()) == ["m06"]


def test_new_menu_item_ids_are_unique_across_restaurants(isolated_menu_repo):
    # r02 already has m03, so a new r01 item must not be given m03.
    every_id = [item["id"] for restaurant in ("r01", "r02")
                for item in isolated_menu_repo.get_menu_data(restaurant)]

    assert isolated_menu_repo.generate_menu_item_id() not in every_id


def test_menu_writes_never_touch_committed_data(client):
    before = COMMITTED_DATA.read_bytes()

    client.post("/restaurant/r01/menu", json=NEW_ITEM)
    client.patch("/restaurant/1/menu/m01", json={"price": 1})
    client.delete("/restaurants/r01/menu/m02")

    assert COMMITTED_DATA.read_bytes() == before


############################################################################################
### #63 Delete a menu item (DELETE)
############################################################################################

def test_delete_menu_item_returns_204_and_removes_it(client, isolated_data_dir):
    response = client.delete("/restaurants/r01/menu/m01")

    assert response.status_code == 204
    assert client.get("/restaurants/r01/menu/m01").status_code == 404
    assert menu_ids(reload_menu(isolated_data_dir, "r01")) == ["m02"]


def test_delete_leaves_other_restaurants_untouched(client, isolated_data_dir):
    before = reload_menu(isolated_data_dir, "r02")
    client.delete("/restaurants/r01/menu/m01")
    assert reload_menu(isolated_data_dir, "r02") == before


@pytest.mark.parametrize("path", ["/restaurants/r01/menu/m99", "/restaurants/unknown/menu/m01",
                                  "/restaurants/r01/menu/m03"])
def test_delete_unknown_item_or_restaurant_returns_404(client, path):
    assert client.delete(path).status_code == 404


def test_repository_remove_unknown_item_raises(isolated_menu_repo):
    with pytest.raises(MenuItemNotFoundError):
        isolated_menu_repo.remove_menu_item("r01", "m99")


def test_service_remove_then_get_raises(isolated_menu_service):
    isolated_menu_service.remove_menu_item("r01", "m02")
    with pytest.raises(MenuItemNotFoundError):
        isolated_menu_service.get_menu_item("r01", "m02")

