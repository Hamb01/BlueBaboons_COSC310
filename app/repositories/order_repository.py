"""Repository layer responsible for reading and writing orders."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.core.exceptions import OrderNotFoundError
from app.repositories.jsonstore import JsonStore


class OrderRepository:
    """Stores orders in data/Orders.json, keyed by stable order id (o01, o02, ...)."""

    # Coding Notes:
    # This class only loads and saves orders, nothing else.
    # The rules about who's allowed to see an order are in OrderService, not here.
    # Everything goes through JsonStore so the file never ends up half written if something crashes.
    # From top to bottom:
    # - get_order                -> one order by id (404 if it doesn't exist)
    # - list_orders_for_customer -> every order one customer placed
    # - generate_order_id        -> next id (o01, o02, ...)
    # - create_order             -> saves a new order, checkout (#101) calls this

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.store = JsonStore(self.data_dir / "Orders.json")
        self.orders: Dict[str, Dict[str, Any]] = self.store.load()

    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        get_order
        -------------------

        Description:
            Reads one order from the persistence layer

        Args:
            order_id : string -> unique ID of the order

        Returns:
            Dict[str, Any] -> the stored order

        Raises:
            OrderNotFoundError -> no order has that id
        """
        if order_id not in self.orders:
            raise OrderNotFoundError(order_id)
        return dict(self.orders[order_id])

    def list_orders_for_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Return every order placed by the customer (in no particular order)."""
        return [dict(order) for order in self.orders.values() if order["customer_id"] == customer_id]

    def generate_order_id(self) -> str:
        """Return the next order id: one past the highest existing oNN id."""
        # same idea as the r01 / m01 ids: find the biggest number we have and add 1
        numbers = [int(key[1:]) for key in self.orders if key.startswith("o") and key[1:].isdigit()]
        return f"o{(max(numbers) + 1) if numbers else 1:02d}"

    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        create_order
        -------------------

        Description:
            Assigns a new id to the order and saves it (used by checkout)

        Args:
            order_data : Dict[str, Any] -> the order without an id

        Returns:
            Dict[str, Any] -> the saved order including its id

        Raises:
            DataPersistenceError -> the order could not be written; nothing is stored
        """
        order_id = self.generate_order_id()
        order = {**order_data, "id": order_id}
        updated = {**self.orders, order_id: order}
        # save to the file first. if the save blows up we never touch self.orders,
        # so a failed checkout doesn't leave a fake order sitting in memory
        self.store.save(updated)
        self.orders = updated
        return dict(order)
