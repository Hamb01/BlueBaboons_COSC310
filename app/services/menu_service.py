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
        """
            get_menu
            -------------------

            Description:
                Retrives menu data from the specified restaurant

            Args: 
                restaurant_id : string -> unique ID belonging to the restaurant in question

            Returns:
                List of Menu Items -> List of all menu items sold by the restaurant (menu items are stored as a dictionary)

            Raises: 
                ValidationError -> The data stored in the restaurant respository is of the wrong shape ***BUG : This will return 422, but it should return 500 ***
                EmptyMenuError -> The restaurant does not have any items on their menu
        """
        menu_data = self.repository.get_menu_data(restaurant_id)
        if not menu_data:
            raise EmptyMenuError(restaurant_id)

        return [
            MenuItem.model_validate(item)
            for item in menu_data
            if item.get("restaurant_id") == restaurant_id
        ]

    def get_menu_item(self, restaurant_id: str, item_id: str) -> MenuItem:
        """
            get_menu_item
            -------------------

            Description:
                Retrieves a single menu item from a specific restaurant

            Args: 
                restaurant_id : string -> unique ID belonging to the restaurant in question
                item_id : string -> unique ID belonging to the menu item in question

            Returns:
                MenuItem -> data related to the specific menu_item (stored as a dictionary)

            Raises: 
                RestaurantNotFoundError -> The Restaurant is not stored in the restaurants.json file
                MenuItemNotFoundError -> The restaurant does not have that
                EmptyMenuError -> The restaurant does not have any items on their menu
        """
        for item in self.get_menu(restaurant_id):
            if item.id == item_id:
                return item
        raise MenuItemNotFoundError(restaurant_id, item_id)

    def add_new_menu_item(
        self,
        restaurant_id: str,
        menu_item: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
            add_new_menu_item
            -------------------

            Description:
                creates a new menu item for a specific restaurant

            Args: 
                restaurant_id : string -> unique ID belonging to the restaurant in question
                menu_item : Dict[str, Any] -> the data pertaining to the menu item that you are creating 

            Returns:
                menu_item : Dict[str, Any] -> the Menu item that you've just created

            Raises: 
                RestaurantNotFoundError -> The Restaurant is not stored in the restaurants.json file
                DataPersistenceError -> There was an error while saving you changes to the Json file
        """
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
         """
            update_menu_item
            -------------------

            Description:
                Update some of the data for an existing menu item for a specific restaurant

            Args: 
                restaurant_id : string -> unique ID belonging to the restaurant in question
                item_id : string -> unique ID belonging to the menu_item in question
                updated_data : Dict[str, Any] -> the data fields that you wish to update

            Returns:
                menu_item : Dict[str, Any] -> the Menu item that you've just updated

            Raises: 
                ValidationError -> Your updated menu_item is in the wrong form
                RestaurantNotFoundError -> The Restaurant is not stored in the restaurants.json file
                MenuItemNotFoundError -> The restaurant does not have that
                DataPersistenceError -> There was an error while saving you changes to the Json file
        """
        current = self.get_menu_item(restaurant_id, item_id)
        changes = {
            key: value for key, value in updated_data.items() if key in EDITABLE_FIELDS
        }
        updated = MenuItem.model_validate({**current.model_dump(), **changes})
        return self.repository.update_menu_item(restaurant_id, item_id, updated.model_dump())

    def remove_menu_item(self, restaurant_id: str, item_id: str) -> None:
        """
            remove_menu_item
            -------------------

            Description:
                Deletes a menu item from a restaurants menu

            Args: 
                restaurant_id : string -> unique ID belonging to the restaurant in question
                item_id : string -> unique ID belonging to the menu_item in question

            Returns:
                void

            Raises: 
                RestaurantNotFoundError -> The Restaurant is not stored in the restaurants.json file
                MenuItemNotFoundError -> The restaurant does not have that
                DataPersistenceError -> There was an error while saving you changes to the Json file
        """
        self.repository.remove_menu_item(restaurant_id, item_id)
