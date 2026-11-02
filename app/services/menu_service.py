"""Service layer for browsing and managing restaurant menus."""

from typing import Any, Dict

from app.core.exceptions import EmptyMenuError, MenuItemNotFoundError
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu_item import MenuItem

# Coding Notes:
# The service layer acts as the business controller for menus.
# The repository layer (MenuRepository) acts as the data access layer.
# From top to bottom:
# - get menu
# - get menu item
# - add new menu item
# - update menu item
# - remove menu item

EDITABLE_FIELDS = ("name", "description", "price", "availability")


class MenuService:
    """Service layer for browsing and managing restaurant menus."""

    def __init__(self, repository: MenuRepository):
        self.repository = repository

    def get_menu(self, restaurant_id: str) -> list[MenuItem]:
        """Return the full menu for a restaurant."""
        menu_data = self.repository.get_menu_data(restaurant_id)
        if not menu_data:
            raise EmptyMenuError(restaurant_id)

        return [
            MenuItem.model_validate(item)
            for item in menu_data
            if item.get("restaurant_id") == restaurant_id
        ]

    def get_menu_item(self, restaurant_id: str, item_id: str) -> MenuItem:
        """Return a single menu item for the named restaurant."""
        for item in self.get_menu(restaurant_id):
            if item.id == item_id:
                return item
        raise MenuItemNotFoundError(restaurant_id, item_id)

    def add_new_menu_item(
        self,
        restaurant_id: str,
        menu_item: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add a new menu item to the specified restaurant."""
        self.repository.get_menu_data(restaurant_id)

        new_menu_item = MenuItem(
            id=self.repository.generate_menu_item_id(),
            restaurant_id=restaurant_id,
            name=menu_item.get("name"),
            description=menu_item.get("description"),
            price=menu_item.get("price", 0.0),
            availability=menu_item.get("availability", True),
        )
        return self.repository.add_menu_item(restaurant_id, new_menu_item.model_dump())

    def update_menu_item(
        self,
        restaurant_id: str,
        item_id: str,
        updated_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update an existing menu item with the supplied fields."""
        current = self.get_menu_item(restaurant_id, item_id)
        changes = {
            key: value for key, value in updated_data.items() if key in EDITABLE_FIELDS
        }
        updated = MenuItem.model_validate({**current.model_dump(), **changes})
        return self.repository.update_menu_item(restaurant_id, item_id, updated.model_dump())

    def remove_menu_item(self, restaurant_id: str, item_id: str) -> None:
        """Remove a menu item from the restaurant's menu."""
        self.repository.remove_menu_item(restaurant_id, item_id)
