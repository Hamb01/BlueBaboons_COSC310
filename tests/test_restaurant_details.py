import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import RestaurantNotFoundError
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant_schema import RestaurantResponse
from app.services.restaurant_service import RestaurantService


def test_service_returns_restaurant_details(
    isolated_restaurant_service: RestaurantService,
):
    result = isolated_restaurant_service.get_restaurant_details("r02")

    assert isinstance(result, RestaurantResponse)
    assert result.id == "r02"
    assert result.name == "Coolio_Sushi"
    assert result.opening_hours == "08:00-21:00"


def test_service_unknown_restaurant_raises(
    isolated_restaurant_service: RestaurantService,
):
    with pytest.raises(RestaurantNotFoundError):
        isolated_restaurant_service.get_restaurant_details("r999")


def test_get_restaurant_details_returns_200(client: TestClient):
    response = client.get("/restaurants/r01")

    assert response.status_code == 200
    assert response.json() == {
        "address": "6767 Leon Ave, Kelowna, BC",
        "postal_code": "V1W 3Z9",
        "id": "r01",
        "name": "Authentic_Tacos",
        "location": "Kelowna",
        "isOpen": True,
        "cuisine": "Mexican",
        "opening_hours": "09:00-21:00",
    }


def test_get_restaurant_details_unknown_id_returns_404(client: TestClient):
    response = client.get("/restaurants/r999")

    assert response.status_code == 404
    assert "r999" in response.json()["message"]


def test_get_restaurant_details_returns_422_for_invalid_postal_code(
        isolated_restaurant_repo: RestaurantRepository, client: TestClient):
    """Verify respository assigns base ID when no records exist."""
    response = client.post("/restaurants", json={
        "name": "Test_Restaurant",
        "location": "Lake Rd",
        "address": "123 Lake Road",
        "postal_code": "v1w aa2",
        "isOpen": True,
        "cuisine": "Seafood",
        "opening_hours": "09:00-21:00"
    })
    assert response.status_code == 422
    isolated_restaurant_repo.restaurants = {}
