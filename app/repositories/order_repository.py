from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.repositories.json_file_store import JsonFileStore


class OrderRepository:
    """Repository layer for orders.

    Owner: Person C (checkout + orders).
    Storage: data/Orders.json
    TODO: what does one stored order look like?
    TODO: should any method ever be allowed to change an order's items or prices after it is saved?
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.store = JsonFileStore(self.data_dir / "Orders.json")

    def create(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("OrderRepository.create")

    def get_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("OrderRepository.get_by_id")

    def list_for_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError("OrderRepository.list_for_customer")
