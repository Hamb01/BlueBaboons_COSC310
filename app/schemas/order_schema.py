"""Schemas for orders created at checkout."""

from typing import Literal

from pydantic import BaseModel, Field

# Coding Notes:
# An order is basically a receipt.
# At checkout we copy each item's name and price into the order, so if a restaurant
# changes its prices later the old order still shows what was actually paid.


class OrderItem(BaseModel):
    """One line of an order, copied from the menu at checkout."""

    menu_item_id: str
    name: str
    unit_price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)


class Order(BaseModel):
    """An order as stored in data/Orders.json and returned by the API."""

    id: str = Field(..., description="Order id, e.g. o01")
    customer_id: str
    restaurant_id: str
    status: Literal["placed"] = "placed"
    delivery_address: str
    items: list[OrderItem]
    subtotal: float = Field(..., ge=0)
    total: float = Field(..., ge=0)
    created_at: str = Field(..., description="When the order was placed (ISO 8601, UTC)")
