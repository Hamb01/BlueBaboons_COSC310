"""Order and checkout routes."""

from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_checkout_service,
    get_current_active_customer,
    get_order_service,
)
from app.schemas.order_schema import Order
from app.services.checkout_service import CheckoutService
from app.services.order_service import OrderService

router = APIRouter(tags=["Orders"])


@router.post(
    "/checkout",
    status_code=status.HTTP_201_CREATED,
    response_model=Order,
    summary="Checkout Active Cart",
    description=(
        "Validates the customer and active cart, revalidates menu items and prices, "
        "persists a new order, and closes/clears the cart only after saving succeeds."
    ),
    responses={
        status.HTTP_201_CREATED: {"description": "Order created from active cart"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Not signed in"},
        status.HTTP_403_FORBIDDEN: {"description": "Account is deactivated or forbidden"},
        status.HTTP_409_CONFLICT: {
            "description": "Cart is missing/empty or a menu item is unavailable/missing"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Failed to persist order; cart remains unchanged"
        },
    },
)
def checkout_cart(
    user=Depends(get_current_active_customer),
    service: CheckoutService = Depends(get_checkout_service),
) -> Order:
    """Create an order from the authenticated customer's active cart."""
    return service.checkout(user.id)


@router.get(
    "/customers/me/orders",
    response_model=list[Order],
    status_code=status.HTTP_200_OK,
    summary="List My Orders",
    description="Returns a list of all orders that the current user has ever placed",
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Not signed in"}},
)
def list_my_orders(
    user=Depends(get_current_active_customer),
    service: OrderService = Depends(get_order_service),
) -> list[Order]:
    """List my orders."""
    return service.list_my_orders(user)


@router.get(
    "/orders/{order_id}",
    response_model=Order,
    status_code=status.HTTP_200_OK,
    summary="Get Order",
    description="Returns a specific order (keyed by unique order ID)",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Not signed in"},
        status.HTTP_403_FORBIDDEN: {"description": "This is another customer's order"},
        status.HTTP_404_NOT_FOUND: {"description": "Order not found"},
    },
)
def get_order(
    order_id: str,
    user=Depends(get_current_active_customer),
    service: OrderService = Depends(get_order_service),
) -> Order:
    """Get one order."""
    return service.get_order(order_id, user)