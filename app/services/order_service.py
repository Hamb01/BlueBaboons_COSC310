"""Service layer for reading orders (#99, #100)."""

from app.core.exceptions import UserNotAuthorizedError
from app.repositories.order_repository import OrderRepository
from app.schemas.order_schema import Order
from app.schemas.user_schema import Developer, RestaurantAdmin, RestaurantOwner, SupportStaff, User

# Coding Notes:
# This is where the order rules live (the repository just saves and loads).
# Who's allowed to look at an order:
# - the customer who placed it
# - developers and support staff, since they deal with every order
# - restaurant owners / admins, but only for orders from their own restaurant
# Everyone else gets a 403.
# We check the role by the user's type (Customer, Developer, ...), which comes from
# the first letter of their id in Users.json (c, d, s, o, a).


class OrderService:
    """Business rules for viewing orders."""

    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def get_order(self, order_id: str, current_user: User) -> Order:
        """
        get_order
        -------------------

        Description:
            Returns one order, if the current user is allowed to see it

        Args:
            order_id : string -> unique ID of the order
            current_user : User -> the signed-in user making the request

        Returns:
            Order -> the order with the names and prices frozen at checkout

        Raises:
            OrderNotFoundError -> no order has that id
            UserNotAuthorizedError -> the order belongs to someone else
        """
        order = Order.model_validate(self.repository.get_order(order_id))
        if not self._can_view(order, current_user):
            raise UserNotAuthorizedError
        return order

    def list_my_orders(self, current_user: User) -> list[Order]:
        """
        list_my_orders
        -------------------

        Description:
            Returns every order the current user has placed, newest first

        Args:
            current_user : User -> the signed-in user making the request

        Returns:
            list[Order] -> the user's orders, or an empty list if there are none

        Raises:
            none
        """
        orders = [Order.model_validate(order)
                  for order in self.repository.list_orders_for_customer(current_user.id)]
        # newest first. if two orders have the exact same time we fall back to the id
        # so the list always comes back in the same order
        return sorted(orders, key=lambda order: (order.created_at, order.id), reverse=True)

    @staticmethod
    def _can_view(order: Order, user: User) -> bool:
        """Apply the access rules listed at the top of this module."""
        if order.customer_id == user.id or isinstance(user, (Developer, SupportStaff)):
            return True
        if isinstance(user, RestaurantOwner):
            return order.restaurant_id in user.owned_restaurants
        if isinstance(user, RestaurantAdmin):
            return order.restaurant_id in user.managed_restaurants
        return False
