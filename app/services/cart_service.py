"""Cart service for handling cart-related operations."""

from typing import Any, Dict, Optional, Protocol

from app.core.exceptions import (
    CartItemNotFoundError,
    CartRestaurantConflictError,
    DomainError,
    MenuItemUnavailableError,
)
from app.schemas.cart_schema import (
    Cart,
    CartItemAdd,
    CartItemQuantityUpdate,
    CartLine,
    CartResponse,
)
from app.services.menu_service import MenuService

# Coding Notes:
# The service owns every cart business rule; the repository only loads and saves carts.
# Carts are stored as plain dicts shaped like the Cart schema.
# Prices are looked up from the menu every time a cart is returned, so totals are never stale.


class CartRepositoryInterface(Protocol):
    """What CartService needs from the cart repository (implemented in cart_repository.py, #95)."""

    def get_active_cart(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Return the customer's active cart, or None if they do not have one."""

    def create_cart(self, customer_id: str) -> Dict[str, Any]:
        """Create, persist and return a new empty active cart with a new id (k01, k02, ...)."""

    def save_cart(self, cart: Dict[str, Any]) -> Dict[str, Any]:
        """Persist the given cart (replacing the stored one with the same id) and return it."""


class CartService:
    """Business rules for a customer's shopping cart."""

    def __init__(self, repository: CartRepositoryInterface, menu_service: MenuService):
        self.repository = repository
        self.menu_service = menu_service

    def get_active_cart(self, customer_id: str) -> CartResponse:
        """
        get_active_cart
        -------------------

        Description:
            Returns the customer's active cart, creating an empty one on the first request

        Args:
            customer_id : string -> unique ID belonging to the customer

        Returns:
            CartResponse -> the cart with current prices and backend-calculated totals

        Raises:
            DataPersistenceError -> the new cart could not be saved
        """
        return self._to_response(self._get_or_create(customer_id))

    def add_item(self, customer_id: str, payload: CartItemAdd) -> CartResponse:
        """
        add_item
        -------------------

        Description:
            Adds a menu item to the customer's active cart. Adding an item that is already in
            the cart increases its quantity instead of adding a second line.

        Args:
            customer_id : string -> unique ID belonging to the customer
            payload : CartItemAdd -> restaurant_id, menu_item_id and quantity (at least 1)

        Returns:
            CartResponse -> the updated cart with backend-calculated totals

        Raises:
            RestaurantNotFoundError -> the restaurant does not exist
            MenuItemNotFoundError -> the menu item does not exist in that restaurant
            EmptyMenuError -> the restaurant has no menu
            MenuItemUnavailableError -> the item exists but cannot be ordered
            CartRestaurantConflictError -> the cart already has items from another restaurant
            DataPersistenceError -> the cart could not be saved
        """
        cart = self._get_or_create(customer_id)
        item = self.menu_service.get_menu_item(payload.restaurant_id, payload.menu_item_id)

        if not item.availability:
            raise MenuItemUnavailableError(payload.restaurant_id, payload.menu_item_id)
        if cart.get("restaurant_id") and cart["restaurant_id"] != payload.restaurant_id:
            raise CartRestaurantConflictError(cart["restaurant_id"], payload.restaurant_id)

        items = [dict(line) for line in cart.get("items", [])]
        for line in items:
            if line["restaurant_id"] == payload.restaurant_id and line["menu_item_id"] == payload.menu_item_id:
                line["quantity"] += payload.quantity
                break
        else:
            items.append({"restaurant_id": payload.restaurant_id,
                          "menu_item_id": payload.menu_item_id,
                          "quantity": payload.quantity})

        updated = Cart.model_validate({**cart, "restaurant_id": payload.restaurant_id, "items": items})
        saved = self.repository.save_cart(updated.model_dump())
        return self._to_response(saved)

    def update_item_quantity(self, customer_id: str, menu_item_id: str, payload: CartItemQuantityUpdate) -> CartResponse:
        """Set the quantity of an existing line in the customer's active cart."""
        cart = self.repository.get_active_cart(customer_id)
        if cart is None:
            raise CartItemNotFoundError(menu_item_id)

        items = [dict(line) for line in cart.get("items", [])]
        for line in items:
            if line["menu_item_id"] == menu_item_id:
                line["quantity"] = payload.quantity
                break
        else:
            raise CartItemNotFoundError(menu_item_id)

        updated = Cart.model_validate({**cart, "items": items})
        saved = self.repository.save_cart(updated.model_dump())
        return self._to_response(saved)

    def remove_item(self, customer_id: str, menu_item_id: str) -> CartResponse:
        """Remove an existing line from the customer's active cart."""
        cart = self.repository.get_active_cart(customer_id)
        if cart is None:
            raise CartItemNotFoundError(menu_item_id)

        existing_items = cart.get("items", [])
        items = [
            dict(line)
            for line in existing_items
            if line["menu_item_id"] != menu_item_id
        ]
        if len(items) == len(existing_items):
            raise CartItemNotFoundError(menu_item_id)

        restaurant_id = cart.get("restaurant_id") if items else None
        updated = Cart.model_validate({**cart, "restaurant_id": restaurant_id, "items": items})
        saved = self.repository.save_cart(updated.model_dump())
        return self._to_response(saved)

    def clear_cart(self, customer_id: str) -> CartResponse:
        """Empty the customer's active cart and release its restaurant association."""
        cart = self.repository.get_active_cart(customer_id)
        if cart is None:
            return self._to_response(self.repository.create_cart(customer_id))

        cleared = Cart.model_validate({**cart, "restaurant_id": None, "items": []})
        saved = self.repository.save_cart(cleared.model_dump())
        return self._to_response(saved)

    def _get_or_create(self, customer_id: str) -> Dict[str, Any]:
        """Return the stored active cart for the customer, creating it if needed."""
        cart = self.repository.get_active_cart(customer_id)
        return cart if cart is not None else self.repository.create_cart(customer_id)

    def _to_response(self, cart: Dict[str, Any]) -> CartResponse:
        """Price every line with the current menu and calculate the totals."""
        stored = Cart.model_validate(cart)
        lines = []
        for line in stored.items:
            try:
                item = self.menu_service.get_menu_item(line.restaurant_id, line.menu_item_id)
                name, price, available = item.name, item.price, item.availability
            except DomainError:
                # The item was removed from the menu after it was added; checkout will reject it.
                name, price, available = "Item no longer on the menu", 0.0, False
            lines.append(CartLine(
                restaurant_id=line.restaurant_id,
                menu_item_id=line.menu_item_id,
                name=name,
                unit_price=price,
                quantity=line.quantity,
                line_total=round(price * line.quantity, 2),
                available=available,
            ))
        subtotal = round(sum(line.line_total for line in lines if line.available), 2)
        return CartResponse(
            id=stored.id,
            restaurant_id=stored.restaurant_id,
            items=lines,
            subtotal=subtotal,
            total=subtotal,
            status=stored.status,
        )
