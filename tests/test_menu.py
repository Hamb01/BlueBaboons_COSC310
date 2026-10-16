import json
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.core.exceptions import MenuItemNotFoundError, RestaurantNotFoundError
from app.schemas.menu_item import MenuItem
from app.services.restaurant_service import RestaurantService


@pytest.mark.parametrize("restaurant_id", ["r01", "r02"])
def test_seed_menus_and_item_details(client, isolated_restaurant_repo, restaurant_id):
    expected = isolated_restaurant_repo.get_menu_data(restaurant_id)
    assert expected
    response = client.get(f"/restaurants/{restaurant_id}/menu")
    assert response.status_code == 200
    assert response.json() == expected
    for item in expected:
        assert MenuItem.model_validate(item).restaurant_id == restaurant_id
        detail = client.get(f"/restaurants/{restaurant_id}/menu/{item['id']}")
        assert detail.status_code == 200
        assert detail.json() == item


@pytest.mark.parametrize("explicit_empty_menu", [True, False])
def test_empty_menu(client, isolated_data_dir, explicit_empty_menu):
    path = isolated_data_dir / "restaurants" / "Authentic_Tacos.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if explicit_empty_menu:
        data["menu"] = []
    else:
        data.pop("menu")
    path.write_text(json.dumps(data), encoding="utf-8")
    response = client.get("/restaurants/r01/menu")
    assert response.status_code == 200
    assert response.json() == []
    assert client.get("/restaurants/r01/menu/m01").status_code == 404


@pytest.mark.parametrize("path", [
    "/restaurants/unknown/menu",
    "/restaurants/unknown/menu/m01",
    "/restaurants/r01/menu/unknown",
    "/restaurants/r01/menu/m03",
    "/restaurants/r02/menu/m01",
])
def test_menu_not_found(client, path):
    assert client.get(path).status_code == 404


def test_service_menu_and_item():
    item = dict(id="item", restaurant_id="restaurant", name="Soup",
                description="Vegetable soup", price=5.25, availability=False)
    repository = Mock()
    repository.get_menu_data.return_value = [item]
    service = RestaurantService(repository)
    assert service.get_menu("restaurant") == [MenuItem(**item)]
    assert service.get_menu_item("restaurant", "item") == MenuItem(**item)
    with pytest.raises(MenuItemNotFoundError):
        service.get_menu_item("restaurant", "missing")


def test_service_rejects_item_from_another_restaurant():
    repository = Mock()
    repository.get_menu_data.return_value = [dict(
        id="item", restaurant_id="other", name="Soup", description="Soup",
        price=5, availability=True,
    )]
    with pytest.raises(MenuItemNotFoundError):
        RestaurantService(repository).get_menu_item("restaurant", "item")


def test_repository_unknown_restaurant(isolated_restaurant_repo):
    with pytest.raises(RestaurantNotFoundError):
        isolated_restaurant_repo.get_menu_data("unknown")


def test_menu_item_rejects_negative_price():
    with pytest.raises(ValidationError):
        MenuItem(id="item", restaurant_id="r01", name="Soup",
                 description="Soup", price=-1, availability=True)
