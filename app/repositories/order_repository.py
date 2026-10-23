from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.repositories.json_file_store import JsonFileStore


class OrderRepository:
    """Repository layer for orders.

    Owner: Person C (checkout + orders).
    Storage: data/Orders.json -> {"o01": {...all OrderResponse fields...}}
    Orders are append-only in M2: once saved, their items and prices are never edited.
    IDs use the prefix 'o' (o01, o02, ...) via JsonFileStore.next_id.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.store = JsonFileStore(self.data_dir / "Orders.json")

    def create(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a new stable ID, save the order, and return it (including the ID)."""
        raise NotImplementedError("OrderRepository.create")

    def get_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Return the stored order, or None if it does not exist."""
        raise NotImplementedError("OrderRepository.get_by_id")

    def list_for_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Return every order placed by this customer, oldest first."""
        raise NotImplementedError("OrderRepository.list_for_customer")
