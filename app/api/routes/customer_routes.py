from fastapi import APIRouter, Depends, status

from app.api.deps import get_customer_service, require_roles
from app.schemas.error_schema import error_responses
from app.schemas.user_schema import (
    CurrentUser,
    CustomerResponse,
    CustomerUpdate,
    DeliveryAddressUpdate,
    UserRole,
)
from app.services.customer_service import CustomerService

# Owner: Person A (customers + auth)
# Routes use /customers/me so a customer can only ever act on their own account.
router = APIRouter(prefix="/customers", tags=["Customers"])

customer_only = require_roles(UserRole.CUSTOMER)


@router.get(
    "/me",
    response_model=CustomerResponse,
    summary="Get my profile",
    responses=error_responses(401, 403),
)
def get_my_profile(
    current_user: CurrentUser = Depends(customer_only),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    return service.get_customer(current_user.id)


@router.patch(
    "/me",
    response_model=CustomerResponse,
    summary="Update my name or email",
    responses=error_responses(401, 403, 409, 422),
)
def update_my_profile(
    payload: CustomerUpdate,
    current_user: CurrentUser = Depends(customer_only),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    return service.update_customer(current_user.id, payload)


@router.put(
    "/me/address",
    response_model=CustomerResponse,
    summary="Replace my default delivery address",
    responses=error_responses(401, 403, 422),
)
def update_my_address(
    payload: DeliveryAddressUpdate,
    current_user: CurrentUser = Depends(customer_only),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    return service.update_delivery_address(current_user.id, payload)


@router.post(
    "/me/deactivate",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate my account",
    responses=error_responses(401, 403),
)
def deactivate_my_account(
    current_user: CurrentUser = Depends(customer_only),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    """The account is kept (not deleted) so past orders stay valid, but it can no longer sign in or order."""
    return service.deactivate_customer(current_user.id)
