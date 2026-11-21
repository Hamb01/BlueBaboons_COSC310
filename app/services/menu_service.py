"""Service layer for browsing and managing restaurant menus."""

from typing import Any, Dict

from app.core.exceptions import EmptyMenuError, MenuItemNotFoundError, MenuItemUnavailableError, UserNotAuthorizedError, UserAuthenticationError
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu_item import MenuItem
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.user_schema import Developer, RestaurantAdmin, RestaurantOwner, User

# Coding Notes:
# The service layer acts as the business controller for menus.
# The repository layer (MenuRepository) acts as the data access layer.
# From top to bottom:
# - get menu
# - get menu item
# - add new menu item
# - update menu item
# - remove menu item

EDITABLE_FIELDS = ("name", "description", "price", "availability", "is_active")


class MenuService:
    """Service layer for browsing and managing restaurant menus."""

    def __init__(self, repository: MenuRepository):
        self.repository = repository
        self.restaurant_repository = RestaurantRepository()

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
            and item.get("is_active", True)
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

    def get_orderable_item(self, restaurant_id: str, item_id: str) -> MenuItem:
        """Return an item only when it is active and currently available."""
        for item_data in self.repository.get_menu_data(restaurant_id):
            if item_data.get("restaurant_id") != restaurant_id:
                continue
            if item_data.get("id") == item_id:
                item = MenuItem.model_validate(item_data)
                if not item.is_active or not item.availability:
                    raise MenuItemUnavailableError(restaurant_id, item_id)
                return item
        raise MenuItemNotFoundError(restaurant_id, item_id)

    def add_new_menu_item(
        self,
        restaurant_id: str,
        menu_item: Dict[str, Any],
        current_user: User | None = None,
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
        self.verify_admin_or_owner(restaurant_id, current_user)
        self.repository.get_menu_data(restaurant_id)

        new_menu_item = MenuItem(
            id=self.repository.generate_menu_item_id(restaurant_id),
            restaurant_id=restaurant_id,
            name=menu_item.get("name"),
            description=menu_item.get("description"),
            price=menu_item.get("price", 0.0),
            availability=menu_item.get("availability", True),
            is_active=menu_item.get("is_active", True),
        )
        return self.repository.add_menu_item(restaurant_id, new_menu_item.model_dump())

    def update_menu_item(
        self,
        restaurant_id: str,
        item_id: str,
        updated_data: Dict[str, Any],
        current_user: User | None = None,
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
        self.verify_admin_or_owner(restaurant_id, current_user)
        current = self.get_menu_item(restaurant_id, item_id)
        changes = {
            key: value for key, value in updated_data.items() if key in EDITABLE_FIELDS
        }
        updated = MenuItem.model_validate({**current.model_dump(), **changes})
        return self.repository.update_menu_item(restaurant_id, item_id, updated.model_dump())

    def remove_menu_item(
        self, restaurant_id: str, item_id: str, current_user: User | None = None
    ) -> None:
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
        self.verify_admin_or_owner(restaurant_id, current_user)
        self.repository.remove_menu_item(restaurant_id, item_id)
    
    
    def verify_admin_or_owner(
        self, restaurant_id: str, current_user: User | None = None
    ) -> None:
        """
            verify_admin_or_owner
            -------------------
        
            Description:
                Verifies if the current user is an admin or the owner of a restaurant. Helper method.
        

            Args: 
                restaurant_id : string -> unique ID belonging to the restaurant in question
                current_user : User -> Information about the currently logged-in user

            Returns:
                Nothing, raises an exception if user isn't authorized.
    
            Raises: 
                RestaurantNotFoundError -> Restaurant isn't stored in the restaurants.json file
                UserNotAuthorizedError -> User isn't an admin or the restaurant's owner, raising 403.
        """
        if current_user is None:
            raise UserAuthenticationError(forbidden_action="restaurant management")
            
        # RestaurantOwner subclasses RestaurantAdmin, so owners must not pass the admin check
        is_admin = (isinstance(current_user, (RestaurantAdmin, Developer))
                    and not isinstance(current_user, RestaurantOwner))

        try:
            restaurant = self.restaurant_repository.get_restaurant_data(restaurant_id)
        except Exception:
            restaurant = None

        owner_id = restaurant.get("owner_id") if restaurant else None
        is_owner = (
            isinstance(current_user, RestaurantOwner)
            and current_user.id == owner_id
        )
        
        if not is_admin and not is_owner:
            raise UserNotAuthorizedError(forbidden_action="restaurant management")