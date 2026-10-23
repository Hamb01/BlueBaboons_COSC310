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
    TODO: write out the checkout steps in order before coding. The spec says what must happen
          and one thing that must NOT happen before the order is saved — which step order satisfies both?
    TODO: if saving fails halfway, what state are the cart and the order left in?
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
        # TODO: what if the price or availability of an item changed since it was added to the cart?
        raise NotImplementedError("OrderService.checkout")

    def get_order(self, order_id: str, current_user: CurrentUser) -> OrderResponse:
        # TODO: who is allowed to see which orders? What status code for someone else's order — and why?
        raise NotImplementedError("OrderService.get_order")

    def list_customer_orders(self, customer_id: str) -> List[OrderResponse]:
        raise NotImplementedError("OrderService.list_customer_orders")
