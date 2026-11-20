"""Cart endpoints for the API."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_cart_service, get_current_active_customer
from app.schemas.cart_schema import (CartItemAdd, CartItemQuantityUpdate, CartResponse)
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


@router.patch(
    "/cart/items/{menu_item_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Cart Item Quantity",
    description="Sets the quantity of an item already in a customer's cart.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
        status.HTTP_403_FORBIDDEN: {"description": "Customer account is deactivated"},
        status.HTTP_404_NOT_FOUND: {"description": "Cart item not found"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Invalid body, e.g. quantity below 1"
        },
    },
)
def update_cart_item_quantity(
    menu_item_id: str,
    payload: CartItemQuantityUpdate,
    customer=Depends(get_current_active_customer),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    """Update an item's quantity and return the updated cart."""
    return service.update_item_quantity(customer.id, menu_item_id, payload)


@router.delete(
    "/cart/items/{menu_item_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove Cart Item",
    description="Removes an item from a customer's active cart.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
        status.HTTP_403_FORBIDDEN: {"description": "Customer account is deactivated"},
        status.HTTP_404_NOT_FOUND: {"description": "Cart item not found"},
    },
)
def remove_cart_item(
    menu_item_id: str,
    customer=Depends(get_current_active_customer),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    """Remove an item and return the updated cart."""
    return service.remove_item(customer.id, menu_item_id)


@router.delete(
    "/cart",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Clear Cart",
    description="Empties the  customer's active cart.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
        status.HTTP_403_FORBIDDEN: {"description": "Customer account is deactivated"},
    },
)
def clear_cart(
    customer=Depends(get_current_active_customer),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    """Clear the customer's cart and return the empty cart."""
    return service.clear_cart(customer.id)
