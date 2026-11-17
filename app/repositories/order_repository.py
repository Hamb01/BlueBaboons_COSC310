"""Repository layer responsible for reading and writing orders."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.core.exceptions import OrderNotFoundError
from app.repositories.jsonstore import JsonStore


class OrderRepository:
    """Stores orders in data/Orders.json with ids o01, o02, ..."""

    # Coding Notes:
    # This class only loads and saves orders. Who can see an order is decided in OrderService.

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.store = JsonStore(self.data_dir / "Orders.json")
        self.orders: Dict[str, Dict[str, Any]] = self.store.load()

    def get_order(self, order_id: str) -> Dict[str, Any]:
        """Return one order, or raise OrderNotFoundError (404)."""
        if order_id not in self.orders:
            raise OrderNotFoundError(order_id)
        return self.orders[order_id]

    def list_orders_for_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Return every order placed by the customer."""
        return [order for order in self.orders.values() if order["customer_id"] == customer_id]

    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Give the order the next id (o01, o02, ...) and save it. Checkout (#101) calls this."""
        order = {**order_data, "id": f"o{len(self.orders) + 1:02d}"}
        # save to the file first, so if the save fails nothing changes in memory either
        self.store.save({**self.orders, order["id"]: order})
        self.orders[order["id"]] = order
        return order
