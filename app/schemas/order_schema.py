"""Schemas for orders created at checkout."""

from typing import Literal

from pydantic import BaseModel, Field

# Coding Notes:
# An order is a snapshot: the item names and unit prices are copied from the menu at
# checkout, so later menu changes never alter an order that was already placed.
# Orders are created by checkout (#101); this milestone only reads them back.


class OrderItem(BaseModel):
    """One line of an order, frozen at checkout."""

    menu_item_id: str = Field(..., description="Menu item id within the order's restaurant")
    name: str = Field(..., description="Item name at the time of checkout")
    unit_price: float = Field(..., ge=0, description="Price per item at the time of checkout")
    quantity: int = Field(..., ge=1, description="How many were ordered")
    line_total: float = Field(..., ge=0, description="unit_price x quantity")


class Order(BaseModel):
    """An order as stored in data/Orders.json and returned by the API."""

    id: str = Field(..., description="Order id, e.g. o01")
    customer_id: str = Field(..., description="Customer who placed the order")
    restaurant_id: str = Field(..., description="Restaurant every item came from")
    status: Literal["placed"] = Field("placed", description="Order status (Milestone 3 adds the full lifecycle)")
    delivery_address: str = Field(..., description="Delivery address at the time of checkout")
    items: list[OrderItem] = Field(..., min_length=1, description="Lines in the order")
    subtotal: float = Field(..., ge=0)
    total: float = Field(..., ge=0)
    created_at: str = Field(..., description="When the order was placed (ISO 8601, UTC)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "o01",
                "customer_id": "c01",
                "restaurant_id": "r01",
                "status": "placed",
                "delivery_address": "213-2532 Shoreline Dr, Lake Country, BC V1V 1V6",
                "items": [{"menu_item_id": "m01", "name": "Beef Taco", "unit_price": 7.99,
                           "quantity": 2, "line_total": 15.98}],
                "subtotal": 15.98,
                "total": 15.98,
                "created_at": "2026-11-17T21:30:00+00:00",
            }
        }
    }
