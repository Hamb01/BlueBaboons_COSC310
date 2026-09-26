from pathlib import Path
from fastapi.testclient import TestClient
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.restaurant_service import RestaurantService

def test_restaurants_added_to_main_dictionary():
    """Verify that all the restaurants added to the restaurant_file_names dictionary also have their keys added to the restaurant_keys dictionary"""
    repo = RestaurantRepository()

    passing = True

    for Key, Value in repo.restaurant_names.items():
        if repo.restaurant_keys.get(Value) != Key:
            passing = False
            break

    assert(passing)

def test_reading_restaurant_data_from_id():
    """Verify that the get_restaurant_data function correctly reads the JSON files"""
    repo = RestaurantRepository()
    data = repo.get_restaurant_data("Authentic_Tacos")

    # following assertions were selected because to get them, you must read the file
    # and they are unlikely to change\
    assert(data.get("restaurant_id") == "r01")
    assert(data.get("restaurant_location") == "Kelowna")
    assert(data.get("restaurant_cuisine") == "Mexican")

def test_reading_restaurant_data_from_restaurant_name():
    """Verify that the get_restaurant_data function correctly reads the JSON files when it must lookup the restaurant id"""
    repo = RestaurantRepository()
    data = repo.get_restaurant_data("r01")

    # following assertions were selected because to get them, you must read the file
    # and they are unlikely to change
    assert(data.get("restaurant_name") == "Authentic_Tacos")
    assert(data.get("restaurant_location") == "Kelowna")
    assert(data.get("restaurant_cuisine") == "Mexican")

def test_restaurant_data_file_contents():
    """Verify that restaurant files contain all the required info"""
    passing = True

    repo = RestaurantRepository()

    for Value in repo.restaurant_names.values():
        print(Value)
        data = repo.get_restaurant_data(Value)
        if not ("restaurant_id" in data and "restaurant_name" in data and
                 "restaurant_location" in data and "restaurant_isOpen" in data and "restaurant_cuisine" in data):
            passing = False
            print(f"Restaurant {Value} is Missing Information")
            break
    assert(passing)

def test_get_restaurant_returns_200_and_ok(client: TestClient):
    """Verify that GET /restaurant returns HTTP 200 with status ok."""
    response = client.get("/restaurant")
    assert response.status_code == 200
    data = (response.json())
    assert (data.get("id") == "r01")

def test_restaurant_service_layer():
    """Test restaurant layer coordinates correctly with repository."""
    service = RestaurantService(RestaurantRepository())
    result = service.get_restaurant_status()
    assert result.id == "r01"