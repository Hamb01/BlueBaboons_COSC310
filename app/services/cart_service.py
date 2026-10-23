from app.core.config import get_settings
from app.repositories.cart_repository import CartRepository
from app.schemas.cart_schema import CartItemAdd, CartResponse
from app.services.customer_service import CustomerService
from app.services.restaurant_service import RestaurantService


class CartService:
    """Service layer for the shopping cart.

    Owner: Person B (cart).
    Reads other subsystems only through their services:
      - customer_service.get_active_customer(...)        -> deactivated customers are rejected
      - restaurant_service.get_restaurant_details(...)   -> restaurant exists / is open
      - restaurant_service.get_menu_item(...)            -> item exists, current price, availability
    Every method returns a CartResponse priced from the *current* menu.
    """

    def __init__(
        self,
        repository: CartRepository,
        restaurant_service: RestaurantService,
        customer_service: CustomerService,
    ):
        self.repository = repository
        self.restaurant_service = restaurant_service
        self.customer_service = customer_service
        self.settings = get_settings()

    def get_cart(self, customer_id: str) -> CartResponse:
        """Return the customer's active cart, creating an empty one if they have none.

        Each customer has at most one active cart.
        """
        raise NotImplementedError("CartService.get_cart")

    def add_item(self, customer_id: str, payload: CartItemAdd) -> CartResponse:
        """Add a menu item (or increase its quantity if it is already in the cart).

        Raises MenuItemNotFoundError, MenuItemUnavailableError, RestaurantClosedError,
        MixedRestaurantCartError (item from a different restaurant), InvalidQuantityError.
        """
        raise NotImplementedError("CartService.add_item")

    def update_item_quantity(self, customer_id: str, menu_item_id: str, quantity: int) -> CartResponse:
        """Set the quantity of an item already in the cart.

        Raises CartItemNotFoundError, InvalidQuantityError.
        """
        raise NotImplementedError("CartService.update_item_quantity")

    def remove_item(self, customer_id: str, menu_item_id: str) -> CartResponse:
        """Remove an item. Removing the last item clears restaurant_id. Raises CartItemNotFoundError."""
        raise NotImplementedError("CartService.remove_item")

    def clear_cart(self, customer_id: str) -> CartResponse:
        """Remove every item and clear restaurant_id."""
        raise NotImplementedError("CartService.clear_cart")

    def validate_for_checkout(self, customer_id: str) -> CartResponse:
        """Revalidate the active cart against current data, for OrderService.checkout.

        Re-reads every menu item (availability + current price) and the restaurant.
        Raises EmptyCartError, MenuItemNotFoundError, MenuItemUnavailableError, RestaurantClosedError.
        Must not modify anything.
        """
        raise NotImplementedError("CartService.validate_for_checkout")

    def close_cart(self, cart_id: str) -> None:
        """Mark the cart checked_out. OrderService calls this only AFTER the order is saved."""
        raise NotImplementedError("CartService.close_cart")
