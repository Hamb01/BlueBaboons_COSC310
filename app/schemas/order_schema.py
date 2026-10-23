from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    """Full lifecycle. M2 only creates PLACED orders; M3 implements the transitions."""
    PLACED = "placed"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    """Snapshot of a cart line at checkout time.

    Name and price are copied, not referenced, so later menu changes
    never alter a past order (historical integrity).
    """
    menu_item_id: str
    name: str
    unit_price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)
    line_total: float = Field(..., ge=0)


class OrderResponse(BaseModel):
    id: str
    customer_id: str
    restaurant_id: str
    restaurant_name: str = Field(..., description="Snapshot of the restaurant name at checkout")
    items: List[OrderItem]
    subtotal: float
    delivery_fee: float
    total: float
    delivery_address: Optional[str] = Field(None, description="Snapshot of the delivery address at checkout")
    status: OrderStatus = OrderStatus.PLACED
    created_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "o01",
                "customer_id": "u01",
                "restaurant_id": "r01",
                "restaurant_name": "Authentic_Tacos",
                "items": [
                    {"menu_item_id": "m01", "name": "Beef Taco", "unit_price": 7.99, "quantity": 2, "line_total": 15.98}
                ],
                "subtotal": 15.98,
                "delivery_fee": 2.99,
                "total": 18.97,
                "delivery_address": "1234 Lakeshore Rd, Kelowna",
                "status": "placed",
                "created_at": "2026-11-01T18:30:00Z",
            }
        }
    }
