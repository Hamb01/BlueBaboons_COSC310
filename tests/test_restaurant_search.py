from fastapi.testclient import TestClient
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant_schema import RestaurantResponse
from app.services.restaurant_service import RestaurantService


def test_list_returns_all_restaurants(client: TestClient):
    """Verify listing without filters returns all restaurants."""

    response = client.get("/restaurants", params={})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "r01"
    assert data[1]["id"] == "r02"


def test_search_matches_name(client: TestClient):
    """Verify name search ignores capitalization."""

    response = client.get("/restaurants", params={'search': 'TACO'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "r01"


def test_search_matches_cuisine(client: TestClient):
    """Verify search matches cuisine and trims spaces."""

    response = client.get("/restaurants", params={'search': ' japanese '})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "r02"


def test_search_matches_location(client: TestClient):
    """Verify search matches part of a location."""

    response = client.get("/restaurants", params={'search': 'rut'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "r02"


def test_cuisine_filter_ignores_case_and_spaces(client: TestClient):
    """Verify cuisine matching ignores capitalization and surrounding spaces."""

    response = client.get("/restaurants", params={'cuisine': ' MEXICAN '})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "r01"


def test_cuisine_filter_requires_exact_match(client: TestClient):
    """Verify a partial cuisine does not match the cuisine filter."""

    response = client.get("/restaurants", params={'cuisine': 'Mex'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
    assert data == []


def test_location_filter_matches_partial_text(client: TestClient):
    """Verify location filtering supports partial text and ignores case and spaces."""

    response = client.get("/restaurants", params={'location': ' KELOW '})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "r01"


def test_open_filter_returns_open_restaurants(client: TestClient):
    """Verify the open filter returns open restaurants."""

    response = client.get("/restaurants", params={'is_open': 'true'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "r01"
    assert data[1]["id"] == "r02"


def test_closed_filter_excludes_open_restaurants(client: TestClient):
    """Verify the closed filter excludes open restaurants."""

    response = client.get("/restaurants", params={'is_open': 'false'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
    assert data == []


def test_unknown_search_returns_empty_list(client: TestClient):
    """Verify a search with no matches returns an empty list."""

    response = client.get("/restaurants", params={'search': 'unknown'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
    assert data == []


def test_empty_text_filters_are_ignored(client: TestClient):
    """Verify empty text filters return all restaurants."""

    response = client.get("/restaurants", params={'search': '   ', 'cuisine': ''})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "r01"
    assert data[1]["id"] == "r02"


def test_combined_filters_return_matching_restaurant(client: TestClient):
    """Verify a restaurant must pass every supplied filter."""

    response = client.get("/restaurants", params={'search': 'sushi', 'cuisine': 'Japanese', 'location': 'rut', 'is_open': 'true'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "r02"


def test_conflicting_filters_return_empty_list(client: TestClient):
    """Verify conflicting filters return no restaurants."""

    response = client.get("/restaurants", params={'search': 'sushi', 'cuisine': 'Mexican'})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
    assert data == []


def test_invalid_open_filter_returns_422(client: TestClient):
    """Verify an invalid open-status filter returns a validation error."""

    response = client.get("/restaurants", params={"is_open": "maybe"})
    assert response.status_code == 422


def test_service_filters_closed_restaurant(
    isolated_restaurant_service: RestaurantService,
    isolated_restaurant_repo: RestaurantRepository,
):
    """Verify the service includes closed restaurants only when requested."""

    isolated_restaurant_repo.restaurants["r01"]["isOpen"] = False

    result = isolated_restaurant_service.list_restaurants(is_open=False)
    assert len(result) == 1
    assert isinstance(result[0], RestaurantResponse)
    assert result[0].id == "r01"

    result = isolated_restaurant_service.list_restaurants(is_open=True)
    assert len(result) == 1
    assert result[0].id == "r02"


def test_empty_restaurant_storage_returns_empty_list(
    client: TestClient,
    isolated_restaurant_repo: RestaurantRepository,
):
    """Verify listing an empty repository returns an empty list."""

    isolated_restaurant_repo.restaurants = {}
    response = client.get("/restaurants")
    assert response.status_code == 200
    assert response.json() == []


def test_search_does_not_change_stored_data(
    client: TestClient,
    isolated_restaurant_repo: RestaurantRepository,
):
    """Verify searching does not write to the restaurant JSON file."""

    before = isolated_restaurant_repo.master_file.read_bytes()
    response = client.get("/restaurants", params={"search": "taco"})
    assert response.status_code == 200
    assert isolated_restaurant_repo.master_file.read_bytes() == before


def test_list_response_contains_restaurant_details(client: TestClient):
    """Verify list results follow the restaurant model and exclude menu data."""

    response = client.get("/restaurants")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for restaurant in data:
        result = RestaurantResponse.model_validate(restaurant)
        assert result.id == restaurant["id"]
        assert "menu" not in restaurant


def test_search_to_details_to_menu(client: TestClient):
    """Verify a customer can search, view restaurant details, and browse menu items."""

    response = client.get("/restaurants", params={"search": "taco"})
    assert response.status_code == 200
    restaurants = response.json()
    assert len(restaurants) == 1
    restaurant = restaurants[0]
    restaurant_id = restaurant["id"]

    response = client.get(f"/restaurants/{restaurant_id}")
    assert response.status_code == 200
    assert response.json() == restaurant

    response = client.get(f"/restaurants/{restaurant_id}/menu")
    assert response.status_code == 200
    menu = response.json()
    assert len(menu) > 0
    item_id = menu[0]["id"]

    response = client.get(f"/restaurants/{restaurant_id}/menu/{item_id}")
    assert response.status_code == 200
    assert response.json() == menu[0]
