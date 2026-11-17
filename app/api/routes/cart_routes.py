"""Cart endpoints for the API."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_cart_service, get_current_active_customer
from app.schemas.cart_schema import CartItemAdd, CartResponse
from app.services.cart_service import CartService

router = APIRouter(tags=["Cart"])


@router.get(
    "/cart",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Active Cart",
    description=(
        "Returns the authenticated customer's active cart. An empty cart is "
        "created on the first request; later calls return the same cart."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
        status.HTTP_403_FORBIDDEN: {"description": "Customer account is deactivated"},
    },
)
def get_cart(
    customer=Depends(get_current_active_customer),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    """Get (or create on first access) the customer's active cart."""
    return service.get_active_cart(customer.id)


@router.post(
    "/cart/items",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Add Item To Cart",
    description=(
        "Adds a menu item to the authenticated customer's active cart. Adding an item that "
        "is already in the cart increases its quantity. All items must come from one restaurant."
    ),
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
        status.HTTP_403_FORBIDDEN: {"description": "Customer account is deactivated"},
        status.HTTP_404_NOT_FOUND: {"description": "Restaurant or menu item not found"},
        status.HTTP_409_CONFLICT: {
            "description": "Item is unavailable, or the cart has items from another restaurant"
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Invalid body, e.g. quantity below 1"},
    },
)
def add_item_to_cart(
    payload: CartItemAdd,
    customer=Depends(get_current_active_customer),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    """Add a menu item to the customer's active cart and return the updated cart."""
    return service.add_item(customer.id, payload)
