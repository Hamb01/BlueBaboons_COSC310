from app.core.config import get_settings
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant_schema import RestaurantResponse




class RestaurantService:
    """Service layer coordinating application health and storage verification."""

    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def get_restaurant_status(self) -> RestaurantResponse:
        information = self.repository.get_restaurant_data();

        return RestaurantResponse(
            id = information.get("restaurant_id"),
            name = information.get("restaurant_name"),
            location = information.get("restaurant_location"),
            isOpen = information.get("restaurant_isOpen"),
            cuisine = information.get("restaurant_cuisine")
        )