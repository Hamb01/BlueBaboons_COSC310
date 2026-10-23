from typing import List

from app.repositories.order_repository import OrderRepository
from app.schemas.order_schema import OrderResponse
from app.schemas.user_schema import CurrentUser
from app.services.cart_service import CartService
from app.services.customer_service import CustomerService
from app.services.restaurant_service import RestaurantService


class OrderService:
    """Service layer for checkout and orders.

    Owner: Person C (checkout + orders).
    Checkout order of operations (this order is a graded business rule):
      1. customer_service.get_active_customer      -> valid customer state
      2. cart_service.validate_for_checkout        -> current prices + availability
      3. build the order snapshot (names, prices, restaurant name, delivery address)
      4. repository.create                         -> persist the order
      5. cart_service.close_cart                   -> ONLY after step 4 succeeded
    """

    def __init__(
        self,
        repository: OrderRepository,
        cart_service: CartService,
        customer_service: CustomerService,
        restaurant_service: RestaurantService,
    ):
        self.repository = repository
        self.cart_service = cart_service
        self.customer_service = customer_service
        self.restaurant_service = restaurant_service

    def checkout(self, customer_id: str) -> OrderResponse:
        """Turn the customer's active cart into a saved order (see steps above)."""
        raise NotImplementedError("OrderService.checkout")

    def get_order(self, order_id: str, current_user: CurrentUser) -> OrderResponse:
        """Return one order.

        Customers may only see their own orders: raise OrderNotFoundError (not 403)
        for someone else's, so order IDs cannot be probed. Admins may see any order.
        """
        raise NotImplementedError("OrderService.get_order")

    def list_customer_orders(self, customer_id: str) -> List[OrderResponse]:
        """Return the customer's order history, oldest first."""
        raise NotImplementedError("OrderService.list_customer_orders")
