from typing import Dict, Any

from app.core.exceptions import MenuItemNotFoundError
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu_item import MenuItem

#Coding Notes:

#The service layer acts as the buisness controller for menus
#The repository layer (MenuRepository) acts as the data access layer

#From top to bottom :
#get menu - returns a list of menu items for a specific restaurant based on its ID
#get menu item - returns the details of a specific menu item for a specific restaurant based on its ID
#add new menu item - adds a new menu item to a specific restaurant
#update menu item - updates an existing menu item for a specific restaurant based on the provided payload
#remove menu item - removes an existing menu item for a specific restaurant based on its ID

# Fields a client may change on an existing menu item.
EDITABLE_FIELDS = ("name", "description", "price", "availability")


class MenuService:
    """Service layer for browsing and managing restaurant menus."""

    def __init__(self, repository: MenuRepository):
        self.repository = repository

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

    def add_new_menu_item(self, restaurant_id: str, menu_item: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new menu item to the specified restaurant.

        The item is validated as a complete MenuItem before anything is written, so an invalid
        item (e.g. a negative price) never reaches the file. New items are available by default.
        """
        self.repository.get_menu_data(restaurant_id)  # RestaurantNotFoundError for an unknown restaurant

        new_menu_item = MenuItem(
            id=self.repository.generate_menu_item_id(),
            restaurant_id=restaurant_id,
            name=menu_item.get("name"),
            description=menu_item.get("description"),
            price=menu_item.get("price", 0.0),
            availability=menu_item.get("availability", True),
        )
        return self.repository.add_menu_item(restaurant_id, new_menu_item.model_dump())

    def update_menu_item(self, restaurant_id: str, item_id: str, updated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing menu item for the specified restaurant.

        Only the fields that were sent change. The merged item is validated before it is saved,
        and an item's id and restaurant_id can never be changed.
        """
        current = self.get_menu_item(restaurant_id, item_id)
        changes = {key: value for key, value in updated_data.items() if key in EDITABLE_FIELDS}
        updated = MenuItem.model_validate({**current.model_dump(), **changes})
        return self.repository.update_menu_item(restaurant_id, item_id, updated.model_dump())

    def remove_menu_item(self, restaurant_id: str, item_id: str) -> None:
        """Remove a menu item; raises MenuItemNotFoundError if it is not on this restaurant's menu."""
        self.repository.remove_menu_item(restaurant_id, item_id)
