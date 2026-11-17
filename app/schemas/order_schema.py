"""Schemas for orders created at checkout."""

from typing import Literal

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    """One item in an order."""

    menu_item_id: str
    name: str
    unit_price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)


class Order(BaseModel):
    """A placed order."""

    id: str = Field(..., description="Order id, e.g. o01")
    customer_id: str
    restaurant_id: str
    status: Literal["placed"] = "placed"
    delivery_address: str
    items: list[OrderItem]
    subtotal: float = Field(..., ge=0)
    total: float = Field(..., ge=0)
    created_at: str = Field(..., description="When the order was placed (ISO 8601, UTC)")
