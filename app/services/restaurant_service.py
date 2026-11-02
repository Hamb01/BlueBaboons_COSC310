"""Service layer coordinating restaurant business logic for the API."""

# Coding Notes:
# The service layer acts as the business controller for the application.
# The repository layer acts as the data access layer.
# Our frontend is the presentation layer.
#
# From top to bottom:
# - list restaurants
# - get restaurant details
# - get all restaurants
# - create restaurant
# - update restaurant
# - menu operations live in menu_service.py

from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant_schema import RestaurantCreate, RestaurantResponse, RestaurantUpdate


class RestaurantService:
    """Service layer coordinates restaurant business logic."""

    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def list_restaurants(
        self,
        search: str | None = None,
        cuisine: str | None = None,
        location: str | None = None,
        is_open: bool | None = None,
    ) -> list[RestaurantResponse]:
        """Return restaurants matching the search criteria."""
        if search is None:
            search = ""
        if cuisine is None:
            cuisine = ""
        if location is None:
            location = ""

        search = search.strip().casefold()
        cuisine = cuisine.strip().casefold()
        location = location.strip().casefold()

        matching_restaurants = []
        all_restaurants = self.repository.get_all_restaurant()

        for data in all_restaurants:
            restaurant = RestaurantResponse.model_validate(data)
            restaurant_name = restaurant.name.casefold()
            restaurant_cuisine = restaurant.cuisine.casefold()
            restaurant_location = restaurant.location.casefold()

            if search != "":
                matches_name = search in restaurant_name
                matches_cuisine = search in restaurant_cuisine
                matches_location = search in restaurant_location

                if not (matches_name or matches_cuisine or matches_location):
                    continue

            if cuisine != "" and cuisine not in ("", restaurant_cuisine):
                continue

            if location != "" and location not in restaurant_location:
                continue

            if is_open is not None and restaurant.isOpen != is_open:
                continue

            matching_restaurants.append(restaurant)

        return matching_restaurants

    def get_restaurant_details(self, restaurant_id: str) -> RestaurantResponse:
        """Return the restaurant details for a specific restaurant id."""
        information = self.repository.get_restaurant_data(restaurant_id)
        return RestaurantResponse.model_validate(information)

    def get_all_restaurants(self) -> list[RestaurantResponse]:
        """Return all restaurant records as validated response models."""
        restaurants_data = self.repository.get_all_restaurant()
        return [RestaurantResponse.model_validate(item) for item in restaurants_data]

    def create_restaurant(self, payload: RestaurantCreate) -> RestaurantResponse:
        """Create a new restaurant and return the stored version."""
        information = self.repository.create_restaurant(payload.model_dump())
        return RestaurantResponse.model_validate(information)

    def update_restaurant(
        self,
        restaurant_id: str,
        payload: RestaurantUpdate,
    ) -> RestaurantResponse:
        """Apply partial updates to an existing restaurant."""
        information = self.repository.update_restaurant(
            restaurant_id,
            payload.model_dump(exclude_unset=True),
        )
        return RestaurantResponse.model_validate(information)
