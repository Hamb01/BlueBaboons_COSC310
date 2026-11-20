from unittest.mock import Mock

import pytest

from app.core.exceptions import UserNotAuthorizedError
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant_schema import RestaurantCreate
from app.schemas.user_schema import Customer, RestaurantOwner
from app.services.restaurant_service import RestaurantService


def test_restaurant_creation_uses_typed_owner_and_rejects_customer():
    repository = Mock()
    repository.create_restaurant.side_effect = lambda data: {**data, "id": "r99"}
    service = RestaurantService(repository)
    payload = RestaurantCreate(
        name="Test Restaurant",
        location="Kelowna",
        address="123 Main St",
        postal_code="V1W 1A1",
        isOpen=True,
        cuisine="Seafood",
        opening_hours="09:00-21:00",
    )
    owner = RestaurantOwner(
        id="o01",
        username="owner",
        name="Test Owner",
        email="owner@example.com",
        password="hashed",
        hash_salt="salt",
        account_is_active=True,
        managed_restaurants=[],
        owned_restaurants=[],
    )
    customer = Customer(
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

    created = service.create_restaurant(payload, owner)

    assert created.owner_id == owner.id
    with pytest.raises(UserNotAuthorizedError):
        service.create_restaurant(payload, customer)

def test_get_restaurants(isolated_restaurant_repo: RestaurantRepository):
    """Verify that the get_restaurant_data function correctly reads the JSON files when it must lookup the restaurant id"""

    data = isolated_restaurant_repo.get_restaurant_data("r01")

    # following assertions were selected because to get them, you must read the file
    # and they are unlikely to change
    assert data["id"] == "r01"
    assert data["name"] == "Authentic_Tacos"
    assert isolated_restaurant_repo.get_restaurant_data("r02")["name"] == "Coolio_Sushi"

def test_restaurants_file_contents(isolated_restaurant_repo: RestaurantRepository):
    """Verify that restaurant files contain all the required info"""

    passing = True

    restaurants = isolated_restaurant_repo.get_all_restaurant()
    id = 0

    for data in restaurants:
        if not {"id", "name", "location", "isOpen", "cuisine", "opening_hours"} <= data.keys():
            passing = False
            print(f"Restaurant {id} is Missing Information")
            break
        id += 1

    assert passing



def test_restaurant_service_layer(isolated_restaurant_service: RestaurantService):
    """Test restaurant layer coordinates correctly with repository."""

    result = isolated_restaurant_service.get_restaurant_details("r01")
    assert result.id == "r01"

def test_id_generation_without_records(
    isolated_restaurant_repo: RestaurantRepository,
):
    """Verify respository assigns base ID when no records exist."""

    isolated_restaurant_repo.restaurants = {}

    new_restaurant = RestaurantCreate(
        name = "Test_Restaurant",
        location = "Lake Rd",
        address = "123 Lake Road",
        postal_code = "v1w 2a3",
        isOpen = True,
        cuisine = "Seafood",
        opening_hours = "09:00-21:00"

    )

    new_restaurant = isolated_restaurant_repo.create_restaurant(
        new_restaurant.model_dump()
    )

    assert new_restaurant["id"] == "r01"
    assert "r01" in isolated_restaurant_repo.restaurants
