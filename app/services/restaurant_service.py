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

    def list_restaurants(
        self,
        search: str | None = None,
        cuisine: str | None = None,
        location: str | None = None,
        is_open: bool | None = None,
    ) -> list[RestaurantResponse]:
        if search is None:
            search = ""
        if cuisine is None:
            cuisine = ""
        if location is None:
            location = ""

        # Remove surrounding spaces and ignore capitalization when comparing.
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

            # Skip this restaurant if the search text matches none of its fields.
            if search != "":
                matches_name = search in restaurant_name
                matches_cuisine = search in restaurant_cuisine
                matches_location = search in restaurant_location

                if not (matches_name or matches_cuisine or matches_location):
                    continue

            if cuisine != "":
                if restaurant_cuisine != cuisine:
                    continue

            if location != "":
                if location not in restaurant_location:
                    continue

            if is_open is not None:
                if restaurant.isOpen != is_open:
                    continue
            matching_restaurants.append(restaurant)

        return matching_restaurants

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

    def add_new_menu_item(self, restaurant_id: str, menu_item: dict) -> MenuItem:
        """Add a new menu item to the specified restaurant."""
        payload = MenuItemCreate.model_validate(menu_item)
        saved_item = self.repository.add_menu_item(restaurant_id, payload.model_dump())
        return MenuItem.model_validate(saved_item)

    def update_menu_item(
        self, restaurant_id: str, item_id: str, updated_data: dict,
        littleBit: bool = False,
    ) -> MenuItem:
        """Update a menu item; littleBit retains the original PUT call convention."""
        if littleBit:
            updated_data = MenuItemCreate.model_validate(updated_data).model_dump()
        else:
            updated_data = MenuItemUpdate.model_validate(updated_data).model_dump(exclude_unset=True)
        updated_item = self.repository.update_menu_item(restaurant_id, item_id, updated_data)
        return MenuItem.model_validate(updated_item)
