"""Repository layer responsible for reading and writing menu data."""

from typing import Any, Dict, List, Optional

from app.core.exceptions import EmptyMenuError, MenuItemNotFoundError, RestaurantNotFoundError
from app.repositories.restaurant_repository import RestaurantRepository


class MenuRepository:
    """Repository layer for menu items stored inside restaurant records."""

    # Coding Notes:
    # The repository layer handles storage and retrieval for menu data.
    # Menus are stored inside each restaurant record in Restaurants.json,
    # so this repository reaches through RestaurantRepository instead of
    # opening the file itself.

    def __init__(self, restaurant_repository: Optional[RestaurantRepository] = None):
        self.restaurant_repository = restaurant_repository or RestaurantRepository()

    def get_menu_data(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """Read a menu only after resolving its restaurant by stable ID."""
        return self.restaurant_repository.get_restaurant_data(restaurant_id).get("menu", [])

    def add_menu_item(self, restaurant_id: str, menu_item: Dict[str, Any]):
        """Add a new menu item to a specific menu."""
        restaurants = self.restaurant_repository.restaurants
        restaurant = restaurants.get(restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError(restaurant_id)

        restaurant_menu = restaurant.get("menu")
        if not restaurant_menu:
            restaurant_menu = []

        restaurant_menu.append(menu_item)
        restaurants[restaurant_id]["menu"] = restaurant_menu

        self.restaurant_repository.save_to_file()
        return menu_item

    def update_menu_item(
        self,
        restaurant_id: str,
        item_id: str,
        item_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Replace the fields of one existing item in place and save it."""
        restaurant_data = self.restaurant_repository.get_restaurant_data(restaurant_id)

        if not restaurant_data.get("menu"):
            raise EmptyMenuError(restaurant_id)

        item = self._find_item(restaurant_id, item_id)
        for key, value in item_data.items():
            if key not in ("id", "restaurant_id"):
                item[key] = value
        self.restaurant_repository.save_to_file()
        return item

    def remove_menu_item(self, restaurant_id: str, item_id: str):
        """Delete a menu item from a restaurant's menu list."""
        restaurants = self.restaurant_repository.restaurants
        try:
            menu = restaurants[restaurant_id].get("menu", [])
        except KeyError as exc:
            raise RestaurantNotFoundError(restaurant_id) from exc

        item_not_found = True
        for item in menu:
            if item["id"] == item_id:
                menu.remove(item)
                item_not_found = False
                break

        if item_not_found:
            raise MenuItemNotFoundError(restaurant_id, item_id)

        restaurants[restaurant_id]["menu"] = menu
        self.restaurant_repository.save_to_file()

    def generate_menu_item_id(self) -> str:
        """Return the next menu item id across all restaurants."""
        existing_ids = []
        for restaurant in self.restaurant_repository.get_all_restaurant():
            for item in restaurant.get("menu", []):
                item_id = item.get("id", "")
                if isinstance(item_id, str) and item_id.startswith("m") and item_id[1:].isdigit():
                    existing_ids.append(int(item_id[1:]))
        next_num = max(existing_ids) + 1 if existing_ids else 1
        return f"m{next_num:02d}"

    def _find_item(self, restaurant_id: str, item_id: str) -> Dict[str, Any]:
        """Find a menu item by id within the restaurant menu."""
        for item in self.get_menu_data(restaurant_id):
            if item.get("id") == item_id:
                return item
        raise MenuItemNotFoundError(restaurant_id, item_id)
