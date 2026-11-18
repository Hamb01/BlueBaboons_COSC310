"""API routes for user collection and detail operations."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_active_customer, get_user_service
from app.schemas.user_schema import CustomerResponse, User
from app.services.user_service import UserService

router = APIRouter(tags=["Customers"])


@router.get(
    "/customers/me",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
)
def get_customer_me(
    current_user: User = Depends(get_current_active_customer),
    service: UserService = Depends(get_user_service),
):
    """
    get_customer_me
    -------------------

    Description:
        returns the information related to the currently authenticated customer

    Returns:
        CustomerResponse -> Information related to the specified customer
    """
    return service.get_customer(current_user.id, current_user)


@router.get(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
)
def get_customer(
    customer_id: str,
    current_user: User = Depends(get_current_active_customer),
    service: UserService = Depends(get_user_service),
):
    """
    get_customer
    -------------------

    Description:
        returns the information related to the customer with the specified ID

    Args:
        customer_id : string -> the id belonging to the specific customer you
            wish to get the data for

    Returns:
        CustomerResponse -> Information related to the specified customer
    """
    return service.get_customer(customer_id, current_user)