import json
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.core.exceptions import MenuItemNotFoundError, RestaurantNotFoundError
from app.schemas.menu_item import MenuItem
from app.services.menu_service import MenuService
from app.core.exceptions import UserNotAuthorizedError
from app.schemas.user_schema import Customer, RestaurantAdmin, RestaurantOwner


def admin_user() -> RestaurantAdmin:
    return RestaurantAdmin(
        id="a01",
        username="admin",
        name="Test Admin",
        email="admin@example.com",
        password="hashed",
        hash_salt="salt",
        account_is_active=True,
        managed_restaurants=["r01", "r02"],
    )


def owner_user() -> RestaurantOwner:
    return RestaurantOwner(
        id="o01",
        username="owner",
        name="Test Owner",
        email="owner@example.com",
        password="hashed",
        hash_salt="salt",
        account_is_active=True,
        owned_restaurants=["r01"],
    )


def customer_user() -> Customer:
    return Customer(
        id="c01",
        username="customer",
        name="Test Customer",
        email="customer@example.com",
        password="hashed",
        hash_salt="salt",
        account_is_active=True,
        address="1 Main St",
        city="Kelowna",
        province="BC",
        postal_code="V1W 1A1",
        balance=0,
    )


@pytest.mark.parametrize("restaurant_id", ["r01", "r02"])
def test_seed_menus_and_item_details(client, isolated_menu_repo, restaurant_id):
    expected = isolated_menu_repo.get_menu_data(restaurant_id)
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
def test_empty_menu(request, isolated_data_dir, explicit_empty_menu):
    path = isolated_data_dir / "Restaurants.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if explicit_empty_menu:
        data["r01"]["menu"] = []
    else:
        data["r01"].pop("menu")
    path.write_text(json.dumps(data), encoding="utf-8")
    # Construct the repository after updating the file: it loads data at startup.
    client = request.getfixturevalue("client")
    response = client.get("/restaurants/r01/menu")
    assert response.status_code == 404
    assert response.json()["message"] == "Restaurant with id r01 has no menu"
    assert response.json()["details"] == "Menu is empty"
    assert client.get("/restaurants/r01/menu/m01").status_code == 404


@pytest.mark.parametrize("path", [
    "/restaurants/unknown/menu",
    "/restaurants/unknown/menu/m01",
    "/restaurants/r01/menu/unknown",
])
def test_menu_not_found(client, path):
    assert client.get(path).status_code == 404


def test_service_menu_and_item():
    item = dict(id="item", restaurant_id="restaurant", name="Soup",
                description="Vegetable soup", price=5.25, availability=False)
    repository = Mock()
    repository.get_menu_data.return_value = [item]
    service = MenuService(repository)
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
        MenuService(repository).get_menu_item("restaurant", "item")


def add_repository_mock():
    """A Mock repository for add tests: r01 exists with an empty menu and the next id is m06."""
    repository = Mock()
    repository.get_menu_data.return_value = []
    repository.generate_menu_item_id.return_value = "m06"
    repository.add_menu_item.side_effect = lambda restaurant_id, item: item
    return repository


def test_service_add_menu_item_converts_price_and_uses_repository():
    repository = add_repository_mock()
    service = MenuService(repository)
    menu_item = {
        "name": "Soup",
        "description": "Vegetable soup",
        "price": "5.25",
        "availability": True,
    }
    expected_item = {
        "id": "m06",
        "restaurant_id": "r01",
        "name": "Soup",
        "description": "Vegetable soup",
        "price": 5.25,
        "availability": True,
    }

    result = service.add_new_menu_item("r01", menu_item, current_user=admin_user())

    assert result == expected_item
    repository.add_menu_item.assert_called_once_with("r01", expected_item)


def test_service_add_menu_item_uses_defaults():
    repository = add_repository_mock()
    service = MenuService(repository)

    result = service.add_new_menu_item(
        "r01", {"name": "Soup", "description": "Vegetable soup"},
        current_user=admin_user()
    )

    assert result["price"] == 0.0
    assert result["availability"] is True
    repository.add_menu_item.assert_called_once_with("r01", result)


def test_service_add_invalid_menu_item_never_reaches_repository():
    repository = add_repository_mock()

    with pytest.raises(ValidationError):
        MenuService(repository).add_new_menu_item(
            "r01", {"name": "Soup", "description": "Soup", "price": -1},
            current_user=admin_user())

    repository.add_menu_item.assert_not_called()


SOUP = {"id": "m01", "restaurant_id": "r01", "name": "Soup",
        "description": "Vegetable soup", "price": 5.25, "availability": True}


def test_service_update_menu_item_saves_merged_item():
    repository = Mock()
    repository.get_menu_data.return_value = [SOUP]
    repository.update_menu_item.side_effect = lambda restaurant_id, item_id, item: item
    service = MenuService(repository)

    result = service.update_menu_item("r01", "m01", {"price": 6.5}, current_user=admin_user())

    assert result == {**SOUP, "price": 6.5}
    repository.update_menu_item.assert_called_once_with("r01", "m01", {**SOUP, "price": 6.5})


def test_service_update_missing_item_raises_not_found():
    repository = Mock()
    repository.get_menu_data.return_value = [SOUP]
    service = MenuService(repository)

    with pytest.raises(MenuItemNotFoundError):
        service.update_menu_item("r01", "missing", {}, current_user=admin_user())


def test_service_remove_menu_item_delegates_to_repository():
    repository = Mock()
    service = MenuService(repository)

    result = service.remove_menu_item("r01", "m01", current_user=admin_user())

    assert result is None
    repository.remove_menu_item.assert_called_once_with("r01", "m01")


def test_repository_unknown_restaurant(isolated_menu_repo):
    with pytest.raises(RestaurantNotFoundError):
        isolated_menu_repo.get_menu_data("unknown")


def test_menu_item_rejects_negative_price():
    with pytest.raises(ValidationError):
        MenuItem(id="item", restaurant_id="r01", name="Soup",
                 description="Soup", price=-1, availability=True)



def test_service_update_returns_repository_item():
    """Updating delegates to the repository without running obsolete file code."""
    repository = Mock()
    repository.get_menu_data.return_value = [SOUP]
    item = {"id": "m01", "restaurant_id": "r01", "name": "Soup",
            "description": "Soup", "price": 6, "availability": True}
    repository.update_menu_item.return_value = item
    service = MenuService(repository)

    assert service.update_menu_item("r01", "m01", {"price": 6}, current_user=admin_user()) == item
    repository.update_menu_item.assert_called_once_with("r01", "m01", {**SOUP, "price": 6})


def test_service_update_missing_item_raises():
    """An item absent from the menu raises the existing not-found error."""
    repository = Mock()
    repository.get_menu_data.return_value = [SOUP]
    with pytest.raises(MenuItemNotFoundError):
        MenuService(repository).update_menu_item("r01", "missing", {"price": 6}, current_user=admin_user())
    repository.update_menu_item.assert_not_called()


def test_menu_authorization_uses_typed_admin_and_owner_users():
    service = MenuService(Mock())
    service.restaurant_repository = Mock()
    service.restaurant_repository.get_restaurant_data.return_value = {"owner_id": "o01"}

    service.verify_admin_or_owner("r01", admin_user())
    service.verify_admin_or_owner("r01", owner_user())
    with pytest.raises(UserNotAuthorizedError):
        service.verify_admin_or_owner("r01", customer_user())
