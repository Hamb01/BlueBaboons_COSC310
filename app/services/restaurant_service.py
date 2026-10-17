from app.core.exceptions import MenuItemNotFoundError
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from app.schemas.restaurant_schema import RestaurantCreate, RestaurantResponse, RestaurantUpdate






class RestaurantService:
    """Service layer coordinating application health and storage verification."""

    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def get_restaurant_status(self) -> RestaurantResponse:
        information = self.repository.get_restaurant_data();

        return RestaurantResponse.model_validate(information)

    def get_restaurant_details(self, restaurant_id: str) -> RestaurantResponse:
        information = self.repository.get_restaurant_data(restaurant_id)
        return RestaurantResponse.model_validate(information)

    def create_restaurant(self, payload: RestaurantCreate) -> RestaurantResponse:
        information = self.repository.create_restaurant(payload)
        return RestaurantResponse.model_validate(information)

    def update_restaurant(
        self, restaurant_id: str, payload: RestaurantUpdate
    ) -> RestaurantResponse:
        information = self.repository.update_restaurant(restaurant_id, payload)
        return RestaurantResponse.model_validate(information)

    def get_menu(self, restaurant_id: str) -> list[MenuItem]:
        return [
            MenuItem.model_validate(item)
            for item in self.repository.get_menu_data(restaurant_id)
            if item.get("restaurant_id") == restaurant_id
        ]

    def get_menu_item(self, restaurant_id: str, item_id: str) -> MenuItem:
        for item in self.get_menu(restaurant_id):
            if item.id == item_id:
                return item
        raise MenuItemNotFoundError(f"Menu item '{item_id}' was not found.")

    def add_new_menu_item(self, restaurant_id: str, payload: MenuItemCreate) -> MenuItem:
        return MenuItem.model_validate(
            self.repository.add_menu_item(restaurant_id, payload.model_dump())
        )

    def update_menu_item(
        self, restaurant_id: str, item_id: str,
        payload: MenuItemCreate | MenuItemUpdate,
    ) -> MenuItem:
        return MenuItem.model_validate(self.repository.update_menu_item(
            restaurant_id, item_id, payload.model_dump(exclude_unset=True)
            if isinstance(payload, MenuItemUpdate) else payload.model_dump(),
        ))
