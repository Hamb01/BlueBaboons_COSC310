from app.repositories.cart_repository import CartRepository
from app.schemas.cart_schema import CartItemAdd, CartResponse
from app.services.customer_service import CustomerService
from app.services.restaurant_service import RestaurantService


class CartService:
    """Service layer for the shopping cart.

    Owner: Person B (cart).
    Other subsystems are injected as services: use them instead of reading their JSON files.
    TODO: list every cross-subsystem rule from the M2 spec (section 4) that this service must enforce.
    """

    def __init__(
        self,
        repository: CartRepository,
        restaurant_service: RestaurantService,
        customer_service: CustomerService,
    ):
        self.repository = repository
        self.restaurant_service = restaurant_service
        self.customer_service = customer_service

    def get_cart(self, customer_id: str) -> CartResponse:
        # TODO: what if the customer has no cart yet? Can they ever have two active carts?
        raise NotImplementedError("CartService.get_cart")

    def add_item(self, customer_id: str, payload: CartItemAdd) -> CartResponse:
        # TODO: what must be checked before an item is allowed into the cart?
        raise NotImplementedError("CartService.add_item")

    def update_item_quantity(self, customer_id: str, menu_item_id: str, quantity: int) -> CartResponse:
        raise NotImplementedError("CartService.update_item_quantity")

    def remove_item(self, customer_id: str, menu_item_id: str) -> CartResponse:
        # TODO: after removing the last item, can the customer start ordering from a different restaurant?
        raise NotImplementedError("CartService.remove_item")

    def clear_cart(self, customer_id: str) -> CartResponse:
        raise NotImplementedError("CartService.clear_cart")

    # TODO (with Person C): what does checkout need from the cart subsystem?
    #   - a way to revalidate the cart against the *current* menu?
    #   - a way to close/clear the cart afterwards — and *when* exactly should that happen?
    # Agree on those method names and signatures here before either of you implements them.
