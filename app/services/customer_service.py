from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import CustomerResponse, CustomerUpdate, DeliveryAddressUpdate


class CustomerService:
    """Service layer for customer profiles and account state.

    Owner: Person A (customers + auth).
    Other services call get_active_customer instead of reading Users.json,
    so the "deactivated customers cannot ..." rule lives in exactly one place.
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_customer(self, customer_id: str) -> CustomerResponse:
        """Return the customer's profile. Raises CustomerNotFoundError."""
        raise NotImplementedError("CustomerService.get_customer")

    def get_active_customer(self, customer_id: str) -> CustomerResponse:
        """Return the customer only if their account is active.

        Raises CustomerNotFoundError, or InactiveAccountError if deactivated.
        Used by CartService and OrderService.
        """
        raise NotImplementedError("CustomerService.get_active_customer")

    def update_customer(self, customer_id: str, payload: CustomerUpdate) -> CustomerResponse:
        """Update name/email (only the fields that were sent).

        Raises EmailAlreadyRegisteredError if the new email belongs to someone else.
        """
        raise NotImplementedError("CustomerService.update_customer")

    def update_delivery_address(self, customer_id: str, payload: DeliveryAddressUpdate) -> CustomerResponse:
        """Replace the customer's default delivery address."""
        raise NotImplementedError("CustomerService.update_delivery_address")

    def deactivate_customer(self, customer_id: str) -> CustomerResponse:
        """Mark the account inactive. The record is kept so past orders stay valid."""
        raise NotImplementedError("CustomerService.deactivate_customer")
