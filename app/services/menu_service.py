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
        """Add a new menu item to the specified restaurant."""

        new_menu_item ={
            "name": menu_item.get("name"),
            "description": menu_item.get("description"),
            "price": float(menu_item.get("price", 0.0)),
            "availability": menu_item.get("availability", False)
        }

        self.repository.update_menu_item(restaurant_id, "", new_menu_item, True)

        return new_menu_item

    def update_menu_item(self, restaurant_id: str, item_id: str, updated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing menu item for the specified restaurant."""

        updated_item = self.repository.update_menu_item(restaurant_id, item_id, updated_data, False)

        if not updated_item:
            raise ValueError(f"Error 404: Menu item not found.")
        return updated_item

    def remove_menu_item(self, restaurant_id: str, item_id: str):
        self.repository.remove_menu_item(restaurant_id, item_id)
