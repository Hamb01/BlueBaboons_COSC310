"""Cart endpoints for the API."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_cart_service, get_current_active_customer
from app.schemas.cart_schema import CartResponse
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