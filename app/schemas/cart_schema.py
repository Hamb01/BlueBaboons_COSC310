"""Schemas for the shopping cart: what is stored, what clients send and what the API returns."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

# Coding Notes:
# Menu item ids are only unique inside one restaurant (each menu starts at m01),
# so a cart line is identified by restaurant_id + menu_item_id.
# Prices are never stored in the cart; responses always use the current menu price.


class CartItem(BaseModel):
    """One line of a stored cart."""

    restaurant_id: str = Field(..., description="Restaurant the menu item belongs to")
    menu_item_id: str = Field(..., description="Menu item id within that restaurant")
    quantity: int = Field(..., ge=1, description="How many of this item are in the cart")


class Cart(BaseModel):
    """A customer's cart as it is persisted by the cart repository."""

    id: str = Field(..., description="Cart id, e.g. k01")
    customer_id: str = Field(..., description="Id of the customer who owns the cart")
    restaurant_id: Optional[str] = Field(
        None, description="Restaurant of every item in the cart; None while the cart is empty"
    )
    items: list[CartItem] = Field(default_factory=list, description="Lines in the cart")
    status: Literal["active", "checked_out"] = Field("active", description="Only active carts can change")


class CartItemAdd(BaseModel):
    """Request body for adding a menu item to the cart."""

    restaurant_id: str = Field(..., description="Restaurant the menu item belongs to")
    menu_item_id: str = Field(..., description="Menu item id within that restaurant")
    quantity: int = Field(1, ge=1, description="How many to add (at least 1)")


class CartLine(BaseModel):
    """One cart line in an API response, priced with the current menu."""

    restaurant_id: str
    menu_item_id: str
    name: str
    unit_price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)
    line_total: float = Field(..., ge=0)
    available: bool = Field(..., description="False if the item is no longer orderable")


class CartResponse(BaseModel):
    """The cart returned by the API, with totals calculated by the backend."""

    id: str
    restaurant_id: Optional[str]
    items: list[CartLine]
    subtotal: float = Field(..., ge=0)
    total: float = Field(..., ge=0)
    status: Literal["active", "checked_out"]

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "k01",
                "restaurant_id": "r01",
                "items": [
                    {
                        "restaurant_id": "r01",
                        "menu_item_id": "m01",
                        "name": "Beef Taco",
                        "unit_price": 7.99,
                        "quantity": 2,
                        "line_total": 15.98,
                        "available": True,
                    }
                ],
                "subtotal": 15.98,
                "total": 15.98,
                "status": "active",
            }
        }
    }
