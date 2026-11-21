"""Checkout orchestration service."""

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Protocol

from app.core.exceptions import (
    AccountNotActiveError,
    CheckoutConflictError,
    DataPersistenceError,
    DomainError,
)
from app.schemas.cart_schema import Cart
from app.schemas.order_schema import Order


class OrderRepositoryCheckoutInterface(Protocol):
    """Persistence contract needed by CheckoutService."""

    def create_order(self, order_data: dict[str, Any]) -> dict[str, Any]:
        """Persist a newly created order and return the saved record."""


def _to_money(value: float | int | Decimal) -> Decimal:
    """Round monetary values consistently to two decimal places."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class CheckoutService:
    """Coordinates customer, cart, menu, order persistence, and cart closure."""

    def __init__(
        self,
        user_service: Any,
        cart_service: Any,
        menu_service: Any,
        order_repository: OrderRepositoryCheckoutInterface,
    ):
        self.user_service = user_service
        self.cart_service = cart_service
        self.menu_service = menu_service
        self.order_repository = order_repository

    def checkout(self, customer_id: str) -> Order:
        """Validate customer, cart, and menu items, save order, then close cart."""
        #Verify customer exists and is active (403 if deactivated)
        customer = self.require_active_customer(customer_id)

        #Retrieve active cart and ensure it exists and is not empty (409)
        raw_cart = self.cart_service.repository.get_active_cart(customer_id)
        if raw_cart is None:
            raise CheckoutConflictError(
                "Cannot check out without an active cart.",
                details=f"No active cart found for customer {customer_id}.",
            )
        cart = Cart.model_validate(raw_cart)
        if not cart.items:
            raise CheckoutConflictError(
                "Cannot check out an empty cart.",
                details="Add at least one available menu item before checking out.",
            )

        #Revalidate every cart item against live menu data & recalculate totals (409 on conflict)
        order_items: list[dict[str, Any]] = []
        subtotal_dec = Decimal("0.00")

        for line in cart.items:
            try:
                item = self.menu_service.get_orderable_item(
                    line.restaurant_id, line.menu_item_id
                )
            except DomainError as exc:
                raise CheckoutConflictError(
                    "One or more cart items are unavailable or no longer exist.",
                    details=(
                        f"Item {line.menu_item_id} from restaurant "
                        f"{line.restaurant_id}: {exc.message}"
                    ),
                ) from exc

            if getattr(item, "is_active", True) is False or getattr(item, "is_available", True) is False:
                raise CheckoutConflictError(
                    "One or more cart items are currently unavailable.",
                    details=f"Item {line.menu_item_id} is inactive or unavailable.",
                )

            unit_price_dec = _to_money(item.price)
            line_total_dec = _to_money(unit_price_dec * Decimal(line.quantity))
            subtotal_dec = _to_money(subtotal_dec + line_total_dec)

            order_items.append(
                {
                    "menu_item_id": item.id,
                    "name": item.name,
                    "unit_price": float(unit_price_dec),
                    "quantity": line.quantity,
                }
            )

        delivery_address = self.extract_delivery_address(customer)
        total_dec = subtotal_dec

        order_payload: dict[str, Any] = {
            "customer_id": customer_id,
            "restaurant_id": cart.restaurant_id,
            "status": "placed",
            "delivery_address": delivery_address,
            "items": order_items,
            "subtotal": float(subtotal_dec),
            "total": float(total_dec),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        #Persist order first; if saving fails (500), do NOT clear or close the cart
        try:
            saved_order = self.order_repository.create_order(order_payload)
        except DomainError:
            raise
        except Exception as exc:
            raise DataPersistenceError("Orders.json", access_type="write") from exc

        order = Order.model_validate(saved_order)

        #Only after the order is saved, close/clear the active cart
        checked_out_cart = Cart.model_validate(
            {
                **cart.model_dump(),
                "status": "checked_out",
            }
        )
        self.cart_service.repository.save_cart(checked_out_cart.model_dump())

        return order

    def require_active_customer(self, customer_id: str) -> Any:
        if hasattr(self.user_service, "require_active"):
            self.user_service.require_active(customer_id)
            return self.user_service.repository.get_user_data_from_id(customer_id)

        customer = self.user_service.get_user_by_id(customer_id)
        if not getattr(customer, "account_is_active", True):
            reason = getattr(customer, "reason_for_deactivation", None) or "Unspecified"
            raise AccountNotActiveError(reason)
        return customer

    @staticmethod
    def extract_delivery_address(customer: Any) -> str:
        address = getattr(customer, "delivery_address", None) or getattr(customer, "address", "")
        if not address:
            raise CheckoutConflictError(
                "Customer delivery address is missing.",
                details="Update your delivery address before placing an order.",
            )
        return str(address)