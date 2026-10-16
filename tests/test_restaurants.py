from pathlib import Path
from fastapi.testclient import TestClient
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.restaurant_service import RestaurantService


def test_get_restaurants(isolated_restaurant_repo: RestaurantRepository):
    """Verify that the get_restaurant_data function correctly reads the JSON files when it must lookup the restaurant id"""

    data = isolated_restaurant_repo.get_restaurant_data("r01")

    # following assertions were selected because to get them, you must read the file
    # and they are unlikely to change
    assert(data[0].get("restaurant_name") == "Authentic_Tacos")
    assert(data[1].get("restaurant_name") == "Coolio_Sushi")

def test_restaurants_file_contents(isolated_restaurant_repo: RestaurantRepository):
    """Verify that restaurant files contain all the required info"""

    passing = True

    restaurants = isolated_restaurant_repo.get_restaurant_data()
    id = 0

    for data in restaurants:
        if not ("restaurant_id" in data and "restaurant_name" in data and
                 "restaurant_location" in data and "restaurant_isOpen" in data and "restaurant_cuisine" in data):
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
    assert(data[0].get("restaurant_name") == "Authentic_Tacos")
    assert(data[1].get("restaurant_name") == "Coolio_Sushi")

def test_restaurant_service_layer(isolated_restaurant_service: RestaurantService):
    """Test restaurant layer coordinates correctly with repository."""
    
    result = isolated_restaurant_service.get_restaurant_status()
    assert result.id == "r01"