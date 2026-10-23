from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import CustomerResponse, CustomerUpdate, DeliveryAddressUpdate


class CustomerService:
    """Service layer for customer profiles and account state.

    Owner: Person A (customers + auth).
    TODO: cart and checkout must reject deactivated customers. How do you make sure that rule
          is written in exactly ONE place instead of being copied into every service?
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_customer(self, customer_id: str) -> CustomerResponse:
        raise NotImplementedError("CustomerService.get_customer")

    def get_active_customer(self, customer_id: str) -> CustomerResponse:
        # TODO: intended for CartService/OrderService — what should it do for a deactivated customer?
        raise NotImplementedError("CustomerService.get_active_customer")

    def update_customer(self, customer_id: str, payload: CustomerUpdate) -> CustomerResponse:
        # TODO: what if the new email already belongs to another account?
        raise NotImplementedError("CustomerService.update_customer")

    def update_delivery_address(self, customer_id: str, payload: DeliveryAddressUpdate) -> CustomerResponse:
        raise NotImplementedError("CustomerService.update_delivery_address")

    def deactivate_customer(self, customer_id: str) -> CustomerResponse:
        # TODO: delete the record or keep it? What happens to that customer's past orders either way?
        raise NotImplementedError("CustomerService.deactivate_customer")
