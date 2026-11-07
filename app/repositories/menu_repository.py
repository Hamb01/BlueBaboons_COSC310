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
        """
            get_menu_data
            -------------------

            Description:
                checks that the restaurant has a menu and returns the menu if it exists

            Args: 
                restaurant_id : string -> Unique ID belonging to the specific restaurant

            Returns:
                List[Dict[str, Any]] -> The menu data from the specified restaurant (menu data stored as a list of menu items)

            Raises: 
                RestaurantNotFoundError -> The restaurant is not stored in our persistence layer
        """
        return self.restaurant_repository.get_restaurant_data(restaurant_id).get("menu", [])

    def add_menu_item(self, restaurant_id: str, menu_item: Dict[str, Any]):
        """
            add_menu_item
            -------------------

            Description:
                creates a new menu item and places it inside the menu for the specified restaurant

            Args: 
                restaurant_id : string -> Unique ID belonging to the specific restaurant
                menu_item : Dict[str, Any] -> details for the menu item (defined in the menu_item schema)

            Returns:
                void

            Raises: 
                RestaurantNotFoundError -> The restaurant is not stored in our persistence layer
                DataPersistenceError -> There was an error when writing to the JSON file
        """
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
        """
            update_menu_item
            -------------------

            Description:
                updates some of the information about a specific menu item

            Args: 
                restaurant_id : string -> Unique ID belonging to the specific restaurant
                item_id : string -> Unique ID belonging to the specific menu item
                item_data : Dict[str, Any] -> data field(s) to be updated

            Returns:
                void

            Raises: 
                RestaurantNotFoundError -> The restaurant is not stored in our persistence layer
                EmptyMenuError -> The restaurant's menu contained no items
                MenuItemNotFoundError -> the specified menu item was not on the menu
                DataPersistenceError -> There was an error when writing to the JSON file
        """
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
        """
            remove_menu_item
            -------------------

            Description:
                Deletes a menu item from a restaurant's menu list

            Args: 
                restaurant_id : string -> Unique ID belonging to the specific restaurant
                item_id : string -> Unique ID belonging to the specific menu item

            Returns:
                void

            Raises: 
                RestaurantNotFoundError -> The restaurant is not stored in our persistence layer
                MenuItemNotFoundError -> the specified menu item was not on the menu
                DataPersistenceError -> There was an error when writing to the JSON file
        """
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
         """
            generate_menu_item_id
            -------------------

            Description:
                Generates an ID for a new menu item

            Args: 
                restaurant_id : string -> Unique ID belonging to the specific restaurant

            Returns:
                string -> the new ID

            Raises: 
                RestaurantNotFoundError -> The restaurant is not stored in our persistence layer
        """
        
        existing_ids = []
        for restaurant in self.restaurant_repository.get_all_restaurant():
            for item in restaurant.get("menu", []):
                item_id = item.get("id", "")
                if isinstance(item_id, str) and item_id.startswith("m") and item_id[1:].isdigit():
                    existing_ids.append(int(item_id[1:]))
        next_num = max(existing_ids) + 1 if existing_ids else 1
        return f"m{next_num:02d}"

    def _find_item(self, restaurant_id: str, item_id: str) -> Dict[str, Any]:
        """
            _find_item
            -------------------

            Description:
                Find a menu item by id within the restaurant menu

            Args: 
                restaurant_id : string -> Unique ID belonging to the specific restaurant
                item_id : string -> Unique ID belonging to the specific restaurant

            Returns:
                Dict[str, Any] -> The data related to the specified menu_item

            Raises: 
                MenuItemNotFoundError -> The restaurant sells no such menu item
        """
        for item in self.get_menu_data(restaurant_id):
            if item.get("id") == item_id:
                return item
        raise MenuItemNotFoundError(restaurant_id, item_id)
