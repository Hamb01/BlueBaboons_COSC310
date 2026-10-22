from pathlib import Path
from fastapi.testclient import TestClient
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.restaurant_service import RestaurantService


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

    assert(passing)

def test_get_restaurant_returns_200_and_ok(client: TestClient):
    """Verify that GET /restaurant returns HTTP 200 with status ok."""

    response = client.get("/restaurant")
    assert response.status_code == 200
    data = (response.json())
    assert data["id"] == "r01"
    assert data["name"] == "Authentic_Tacos"

def test_restaurant_service_layer(isolated_restaurant_service: RestaurantService):
    """Test restaurant layer coordinates correctly with repository."""
    service = RestaurantService(RestaurantRepository())
    result = service.get_restaurant_status()
    assert result.id == "r01"


#Case where I tested the business logic where everything goes right
def test_business_logic():
    """Test business logic for adding and updating menu items."""
    service = RestaurantService(RestaurantRepository())
    # Add assertions for the business logic tests
    passing = True
    try:
        # Test adding a new menu item
        new_item = {
            "name": "Test Item",
            "price": 9.99,
            "description": "A test menu item",
            "category": "Test Category"
        }
        added_item = service.add_new_menu_item("r01", new_item)
        assert added_item["name"] == new_item["name"]

        # Test updating an existing menu item
        updated_data = {
            "name": "Updated Test Item",
            "price": 12.99
        }
        updated_item = service.update_menu_item("r01", added_item["id"], updated_data)
        assert updated_item["name"] == updated_data["name"]
        assert updated_item["price"] == updated_data["price"]
    except Exception as e:
        passing = False
        print(f"Error occurred while testing business logic: {e}")

    assert passing
