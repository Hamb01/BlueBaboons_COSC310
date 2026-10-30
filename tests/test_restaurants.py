from pathlib import Path
from fastapi.testclient import TestClient
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.restaurant_service import RestaurantService
from app.schemas.restaurant_schema import RestaurantCreate

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
    
    result = isolated_restaurant_service.get_restaurant_status()
    assert result.id == "r01"

def test_id_generation_without_records(
    isolated_restaurant_repo: RestaurantRepository,
):
    """Verify respository assigns base ID when no records exist."""
    
    isolated_restaurant_repo.restaurants = {}
    
    new_restaurant = RestaurantCreate(
        name = "Test_Restaurant",
        location = "Lake Rd",
        isOpen = True,
        cuisine = "Seafood",
        opening_hours = "09:00-21:00"
        
    )
    
    new_restaurant = isolated_restaurant_repo.create_restaurant(
        new_restaurant.model_dump()
    )
    
    assert new_restaurant["id"] == "r01"
    assert "r01" in isolated_restaurant_repo.restaurants