"""Order endpoints for the API."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_active_customer, get_order_service
from app.schemas.order_schema import Order
from app.services.order_service import OrderService

# Coding Notes:
# - GET /customers/me/orders -> all of my orders, newest first
# - GET /orders/{order_id}   -> one order
# No try/except needed: the exception handler in main.py turns our errors into 403 / 404.

router = APIRouter(tags=["Orders"])


@router.get(
    "/customers/me/orders",
    response_model=list[Order],
    summary="List My Orders",
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Not signed in"}},
)
def list_my_orders(user=Depends(get_current_active_customer),
                   service: OrderService = Depends(get_order_service)) -> list[Order]:
    """Return the signed-in customer's orders, newest first."""
    return service.list_my_orders(user)


@router.get(
    "/orders/{order_id}",
    response_model=Order,
    summary="Get Order",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Not signed in"},
        status.HTTP_403_FORBIDDEN: {"description": "This is another customer's order"},
        status.HTTP_404_NOT_FOUND: {"description": "Order not found"},
    },
)
def get_order(order_id: str, user=Depends(get_current_active_customer),
              service: OrderService = Depends(get_order_service)) -> Order:
    """Return one order if the signed-in user is allowed to see it."""
    return service.get_order(order_id, user)
