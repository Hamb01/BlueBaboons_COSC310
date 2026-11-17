"""Repository layer responsible for reading and writing menu data."""

from typing import Any, Dict, Optional

from app.core.exceptions import EmptyMenuError, MenuItemNotFoundError, RestaurantNotFoundError
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.cart_schema import Cart, CartItem
from app.repositories.user_repository import UserRepository

class CartRepository:
    """Repository layer for menu items stored inside restaurant records."""

    # Coding Notes:
    # The repository layer handles storage and retrieval for menu data.
    # Menus are stored inside each restaurant record in Restaurants.json,
    # so this repository reaches through RestaurantRepository instead of
    # opening the file itself.


#Init handles the two repositories for the user (connected to the cart) and the restaurant repository (connected to the menu items). This allows for the cart repository to access both the user and restaurant data as needed.
    def __init__(self, user_repository: Optional[UserRepository] = None,
                restaurant_repository: Optional[RestaurantRepository] = None):
        self.user_repository = user_repository or UserRepository()
        self.restaurant_repository = restaurant_repository or RestaurantRepository()

    def get_cart(self, user_id: str) -> Cart:
        """
        get_cart_data
        -------------------

        Description:
            checks  and returns if the cart data if it exists else makes a new cart for the user

        Args: 
            user_id : string -> Unique ID belonging to the specific user

        Returns:
            List[Dict[str, Any]] -> The cart data from the specified user

        Raises: 
            RestaurantNotFoundError -> The restaurant is not stored in our persistence layer
        """
        ##Changed When Json store is merged with the user data, this will be changed to get the cart data from the user repository instead of the restaurant repository
        the_cart = self.user_repository.get_user_data(user_id).get("cart", None)
        if the_cart is None:
            new_cart = Cart(user_id=user_id, restaurant_id=None, items=[])
            self.user_repository.add_cart(user_id, new_cart.dict())
            return new_cart
        return Cart.model_validate(the_cart)
        """
        add_item
        -------------------

        Description:
            adds a new item to the user's cart

        Args:
            user_id : string -> Unique ID belonging to the specific user
            cart_item : CartItem -> details for the cart item (defined in the cart_item schema)
            restaurant_id : string -> Unique ID belonging to the specific restaurant
            menu_item_id : string -> Unique ID belonging to the specific menu item

        Returns:
            void

        Raises:
            RestaurantNotFoundError -> The restaurant is not stored in our persistence layer
            DataPersistenceError -> There was an error when writing to the JSON file
        """
def save_cart(self, cart: Cart) -> None:
    user_data = self.user_repository.get_user_data(cart.user_id)
    user_data["cart"] = cart.dict()
    self.user_repository.save_to_file()
            ##will replace with the json when merged with main
def add_item(self, user_id: str, cart_item: CartItem, restaurant_id: str, menu_item_id: str, quantity: int = 1) -> None:
        """Add a menu item to user's cart"""
        # Check if the restaurant exists
        self.restaurant_repository.get_restaurant_data(restaurant_id)
        new_item  = CartItem(menu_item_id=menu_item_id, quantity=quantity)
        self._get_menu_item(restaurant_id, menu_item_id)  # Validate that the menu item exists
        cart = self.get_cart(user_id)
        if cart.restaurant_id not in (None, restaurant_id):
            raise ValueError("Cannot add items from different restaurants to the same cart.")
        for item in cart.items:
            if item.item_id == cart_item.item_id:
                item.quantity += cart_item.quantity
                break
        else:
            cart.items.append(cart_item)
        cart.restaurant_id = restaurant_id
        self.save_cart(cart)
        return cart

def clear_cart(self, user_id: str) -> None:
        """Clear all items from user's cart"""
        cart = self.get_cart(user_id)
        cart.items.clear()
        cart.restaurant_id = None
        self.save_cart(cart)
        return cart


def _get_menu_item(self, restaurant_id: str, menu_item_id: str) -> Dict[str, Any]:
        """Retrieve a menu item from a restaurant's menu"""
        menu = self.restaurant_repository.get_menu_data(restaurant_id)
        for item in menu:
            if item.get("id") == menu_item_id:
                return item
        raise MenuItemNotFoundError(restaurant_id, menu_item_id)

def remove_item(self, user_id: str, menu_item_id: str) -> None:
        """Remove a menu item from user's cart"""
        cart = self.get_cart(user_id)
        for item in cart.items:
            if item.item_id == menu_item_id:
                cart.items.remove(item)
                break
        else:
            raise MenuItemNotFoundError(cart.restaurant_id, menu_item_id)
        if not cart.items:
            cart.restaurant_id = None
        self.save_cart(cart)
        return cart