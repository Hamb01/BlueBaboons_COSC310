from typing import List

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_order_service, require_roles
from app.schemas.error_schema import error_responses
from app.schemas.order_schema import OrderResponse
from app.schemas.user_schema import CurrentUser, UserRole
from app.services.order_service import OrderService

# Owner: Person C (checkout + orders)
router = APIRouter(prefix="/orders", tags=["Orders"])

customer_only = require_roles(UserRole.CUSTOMER)


@router.post(
    "/checkout",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Check out my active cart",
    responses=error_responses(401, 403, 404, 409),
)
def checkout(
    current_user: CurrentUser = Depends(customer_only),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Revalidates the cart against current menu data, saves the order, then closes the cart."""
    return service.checkout(current_user.id)


@router.get(
    "",
    response_model=List[OrderResponse],
    summary="List my order history",
    responses=error_responses(401, 403),
)
def list_my_orders(
    current_user: CurrentUser = Depends(customer_only),
    service: OrderService = Depends(get_order_service),
) -> List[OrderResponse]:
    return service.list_customer_orders(current_user.id)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get one order",
    responses=error_responses(401, 404),
)
def get_order(
    order_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Customers only see their own orders (404 otherwise); admins can see any order."""
    return service.get_order(order_id, current_user)
