from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.repositories.json_file_store import JsonFileStore


class CartRepository:
    """Repository layer for shopping carts.

    Owner: Person B (cart).
    Storage: data/Carts.json -> {"c01": {"id", "customer_id", "restaurant_id", "status",
                                         "items": [{"menu_item_id", "quantity"}]}}
    Only menu_item_id and quantity are stored per line: names and prices are always
    read fresh from the menu by CartService, so totals can never go stale.
    IDs use the prefix 'c' (c01, c02, ...) via JsonFileStore.next_id.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.store = JsonFileStore(self.data_dir / "Carts.json")

    def get_active_for_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Return the customer's cart with status 'active', or None if they have none."""
        raise NotImplementedError("CartRepository.get_active_for_customer")

    def create(self, customer_id: str) -> Dict[str, Any]:
        """Create, save, and return a new empty active cart for the customer."""
        raise NotImplementedError("CartRepository.create")

    def save(self, cart: Dict[str, Any]) -> Dict[str, Any]:
        """Replace the stored cart that has cart['id'] with this one, and return it."""
        raise NotImplementedError("CartRepository.save")
