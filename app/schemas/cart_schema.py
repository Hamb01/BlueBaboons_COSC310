from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class CartStatus(str, Enum):
    ACTIVE = "active"
    CHECKED_OUT = "checked_out"


############################################################################################
### Requests
############################################################################################

class CartItemAdd(BaseModel):
    # Menu item IDs are only unique within a restaurant, so both IDs are required.
    restaurant_id: str = Field(..., description="Restaurant the menu item belongs to")
    menu_item_id: str = Field(..., description="Menu item to add")
    quantity: int = Field(1, ge=1, description="How many to add (the service also enforces the maximum)")


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1, description="New quantity for the item")


############################################################################################
### Responses
############################################################################################

class CartItem(BaseModel):
    menu_item_id: str
    name: str
    unit_price: float = Field(..., ge=0, description="Current menu price, read from the menu")
    quantity: int = Field(..., ge=1)
    line_total: float = Field(..., ge=0, description="unit_price * quantity, calculated by the backend")


class CartResponse(BaseModel):
    """A customer's cart with backend-calculated totals.

    restaurant_id is None while the cart is empty; the first item added sets it.
    """
    id: str
    customer_id: str
    restaurant_id: Optional[str] = None
    status: CartStatus = CartStatus.ACTIVE
    items: List[CartItem] = []
    subtotal: float = 0.0
    delivery_fee: float = 0.0
    total: float = 0.0

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "c01",
                "customer_id": "u01",
                "restaurant_id": "r01",
                "status": "active",
                "items": [
                    {"menu_item_id": "m01", "name": "Beef Taco", "unit_price": 7.99, "quantity": 2, "line_total": 15.98}
                ],
                "subtotal": 15.98,
                "delivery_fee": 2.99,
                "total": 18.97,
            }
        }
    }
