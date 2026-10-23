from fastapi import APIRouter, Depends, status

from app.api.deps import get_customer_service, require_roles
from app.schemas.user_schema import (
    CurrentUser,
    CustomerResponse,
    CustomerUpdate,
    DeliveryAddressUpdate,
    UserRole,
)
from app.services.customer_service import CustomerService

# Owner: Person A (customers + auth)
# TODO: these paths are a PROPOSAL — agree on them in the contracts PR review.
# TODO: document each route's error responses in OpenAPI once you know them (see error_schema.py).
router = APIRouter(prefix="/customers", tags=["Customers"])

customer_only = require_roles(UserRole.CUSTOMER)


@router.get(
    "/me",
    response_model=CustomerResponse,
    summary="Get my profile",
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
)
def deactivate_my_account(
    current_user: CurrentUser = Depends(customer_only),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    return service.deactivate_customer(current_user.id)
