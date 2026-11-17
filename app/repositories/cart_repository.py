"""Repository layer responsible for reading and writing shopping carts."""

from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.repositories.jsonstore import JsonStore
from app.schemas.cart_schema import Cart


class CartRepository:
    """Stores carts in data/Carts.json, keyed by stable cart id (k01, k02, ...)."""

    # Coding Notes:
    # This class only loads and saves carts. All the cart rules (one restaurant per cart,
    # unavailable items, merging quantities, totals) live in CartService.
    # These three methods are exactly what CartService calls (see CartRepositoryInterface
    # in app/services/cart_service.py).
    # From top to bottom:
    # - get_active_cart -> the customer's active cart, or None if they don't have one yet
    # - create_cart     -> makes and saves a new empty cart
    # - save_cart       -> saves a cart (replaces the stored one with the same id)

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.store = JsonStore(self.data_dir / "Carts.json")
        self.carts: Dict[str, Dict[str, Any]] = self.store.load()

    def get_active_cart(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Return the customer's active cart, or None if they do not have one."""
        for cart in self.carts.values():
            if cart["customer_id"] == customer_id and cart["status"] == "active":
                return dict(cart)
        return None

    def create_cart(self, customer_id: str) -> Dict[str, Any]:
        """Create, save and return a new empty active cart with the next id (k01, k02, ...)."""
        # same idea as the r01 / o01 ids: find the biggest number we have and add 1
        numbers = [int(key[1:]) for key in self.carts if key.startswith("k") and key[1:].isdigit()]
        cart_id = f"k{(max(numbers) + 1) if numbers else 1:02d}"
        return self.save_cart(Cart(id=cart_id, customer_id=customer_id).model_dump())

    def save_cart(self, cart: Dict[str, Any]) -> Dict[str, Any]:
        """Save the cart (replacing the stored one with the same id) and return it."""
        updated = {**self.carts, cart["id"]: dict(cart)}
        # save to the file first. if the save fails we never touch self.carts
        self.store.save(updated)
        self.carts = updated
        return dict(cart)
