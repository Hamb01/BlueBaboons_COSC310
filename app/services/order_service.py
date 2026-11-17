"""Service layer for viewing orders (#99, #100)."""

from app.core.exceptions import UserNotAuthorizedError
from app.repositories.order_repository import OrderRepository
from app.schemas.order_schema import Order
from app.schemas.user_schema import Customer, User

# Coding Notes:
# Customers can only see their own orders. Staff accounts (anything that isn't a
# Customer, like developers or support staff) can see every order.


class OrderService:
    """Business rules for viewing orders."""

    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def get_order(self, order_id: str, current_user: User) -> Order:
        """Return one order. 404 if it doesn't exist, 403 if it's another customer's."""
        order = Order.model_validate(self.repository.get_order(order_id))
        if isinstance(current_user, Customer) and order.customer_id != current_user.id:
            raise UserNotAuthorizedError
        return order

    def list_my_orders(self, current_user: User) -> list[Order]:
        """Return the current user's orders, newest first ([] if none)."""
        orders = [Order.model_validate(order)
                  for order in self.repository.list_orders_for_customer(current_user.id)]
        return sorted(orders, key=lambda order: order.created_at, reverse=True)
