"""Order repository."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from app.repositories.generate_id_method import make_id_generator
from app.core.config import get_settings
from app.core.exceptions import OrderNotFoundError
from app.repositories.jsonstore import JsonStore


class OrderRepository:
    """Reads and writes data/Orders.json."""

    _new_id = staticmethod(make_id_generator("o"))  # o01, o02, ...

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.store = JsonStore(self.data_dir / "Orders.json")
        self.orders: Dict[str, Dict[str, Any]] = self.store.load()

    def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get an order by id."""
        if order_id not in self.orders:
            raise OrderNotFoundError(order_id)
        return self.orders[order_id]

    def list_orders_for_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a customer."""
        return [order for order in self.orders.values() if order["customer_id"] == customer_id]

    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new order."""
        order = {**order_data, "id": self._new_id(self.orders.keys())}
        self.store.save({**self.orders, order["id"]: order})
        self.orders[order["id"]] = order
        return order
