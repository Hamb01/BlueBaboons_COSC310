"""API routes for restaurant collection and detail operations."""

# Coding Notes:
# Basic CRUD operations for restaurants (menu item routes live in menu_routes.py).
# From top to bottom:
# - list restaurants
# - get restaurant details
# - create restaurant
# - update restaurant
#
# Each API endpoint and what they do:
# - GET retrieves restaurant data from the backend store
# - POST creates a new restaurant from the provided payload
# - PUT updates an existing restaurant based on the provided payload

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_restaurant_service
from app.schemas.restaurant_schema import RestaurantCreate, RestaurantResponse, RestaurantUpdate
from app.services.restaurant_service import RestaurantService

router = APIRouter(tags=["Restaurant"])


@router.get(
    "/restaurants",
    response_model=list[RestaurantResponse],
    status_code=status.HTTP_200_OK,
    summary="List, search, and filter restaurants",
)
def list_restaurants(
    search: str | None = Query(
        default=None,
        description="Substring search name, cuisine, or location (ignore case)",
    ),
    cuisine: str | None = Query(
        default=None,
        description="Cuisine exact search (ignore case)",
    ),
    location: str | None = Query(
        default=None,
        description="Substring of location (ignore case)",
    ),
    is_open: bool | None = Query(default=None, description="Filter by status"),
    service: RestaurantService = Depends(get_restaurant_service),
) -> list[RestaurantResponse]:
    """Return restaurants matching the requested filters."""
    return service.list_restaurants(search, cuisine, location, is_open)


@router.get(
    "/restaurants/{restaurant_id}",
    response_model=RestaurantResponse,
    status_code=status.HTTP_200_OK,
)
def get_restaurant_details(
    restaurant_id: str,
    service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantResponse:
    """Return restaurant details for the matching restaurant id."""
    return service.get_restaurant_details(restaurant_id)


@router.post("/restaurants", status_code=status.HTTP_201_CREATED)
def create_restaurant(
    payload: RestaurantCreate,
    service: RestaurantService = Depends(get_restaurant_service),
):
    """Create a new restaurant from the provided payload."""
    return service.create_restaurant(payload)


@router.put("/restaurants/{restaurant_id}", status_code=status.HTTP_200_OK)
def update_restaurant(
    restaurant_id: str,
    payload: RestaurantUpdate,
    service: RestaurantService = Depends(get_restaurant_service),
):
    """Update an existing restaurant with the provided fields."""
    return service.update_restaurant(restaurant_id, payload)
