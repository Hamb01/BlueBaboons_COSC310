from fastapi import APIRouter, Depends, status

from app.api.deps import get_cart_service, require_roles
from app.schemas.cart_schema import CartItemAdd, CartItemUpdate, CartResponse
from app.schemas.user_schema import CurrentUser, UserRole
from app.services.cart_service import CartService

# Owner: Person B (cart)
# TODO: these paths are a PROPOSAL — agree on them in the contracts PR review.
# TODO: document each route's error responses in OpenAPI once you know them (see error_schema.py).
router = APIRouter(prefix="/cart", tags=["Cart"])

customer_only = require_roles(UserRole.CUSTOMER)


@router.get(
    "",
    response_model=CartResponse,
    summary="Get (or create) my active cart",
)
def get_my_cart(
    current_user: CurrentUser = Depends(customer_only),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    return service.get_cart(current_user.id)


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a menu item to my cart",
)
def add_cart_item(
    payload: CartItemAdd,
    current_user: CurrentUser = Depends(customer_only),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    return service.add_item(current_user.id, payload)


@router.patch(
    "/items/{menu_item_id}",
    response_model=CartResponse,
    summary="Change the quantity of an item in my cart",
)
def update_cart_item(
    menu_item_id: str,
    payload: CartItemUpdate,
    current_user: CurrentUser = Depends(customer_only),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    return service.update_item_quantity(current_user.id, menu_item_id, payload.quantity)


@router.delete(
    "/items/{menu_item_id}",
    response_model=CartResponse,
    summary="Remove an item from my cart",
)
def remove_cart_item(
    menu_item_id: str,
    current_user: CurrentUser = Depends(customer_only),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    return service.remove_item(current_user.id, menu_item_id)


@router.delete(
    "",
    response_model=CartResponse,
    summary="Clear my cart",
)
def clear_my_cart(
    current_user: CurrentUser = Depends(customer_only),
    service: CartService = Depends(get_cart_service),
) -> CartResponse:
    return service.clear_cart(current_user.id)
