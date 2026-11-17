"""Order endpoints for the API."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_active_customer, get_order_service
from app.schemas.order_schema import Order
from app.services.order_service import OrderService

router = APIRouter(tags=["Orders"])


@router.get(
    "/customers/me/orders",
    response_model=list[Order],
    status_code=status.HTTP_200_OK,
    summary="List My Orders",
    description="Returns every order the signed-in customer has placed, newest first ([] if none).",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
        status.HTTP_403_FORBIDDEN: {"description": "Account is deactivated"},
    },
)
def list_my_orders(
    user=Depends(get_current_active_customer),
    service: OrderService = Depends(get_order_service),
) -> list[Order]:
    """Return the signed-in customer's order history."""
    return service.list_my_orders(user)


@router.get(
    "/orders/{order_id}",
    response_model=Order,
    status_code=status.HTTP_200_OK,
    summary="Get Order",
    description=(
        "Returns one order with the item names and prices frozen at checkout. Customers can "
        "only see their own orders; staff can see any order; restaurant owners and admins can "
        "see orders for their restaurants."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
        status.HTTP_403_FORBIDDEN: {"description": "Order belongs to someone else, or account is deactivated"},
        status.HTTP_404_NOT_FOUND: {"description": "Order not found"},
    },
)
def get_order(
    order_id: str,
    user=Depends(get_current_active_customer),
    service: OrderService = Depends(get_order_service),
) -> Order:
    """Return one order if the signed-in user may see it."""
    return service.get_order(order_id, user)
