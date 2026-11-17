"""Schemas for Cart, cartItem, and cartResponse"""

from typing import Any, Dict, List

from pydantic import BaseModel, Field

class CartItem(BaseModel):
    """A single item in a cart."""
    item_id: str = Field(..., description="Unique ID for the menu item")
    quantity: int = Field(1, gt=0, description="The quantity of this item in the cart")

class Cart(BaseModel):
    """A single cart."""
    user_id: str = Field(..., description="Unique ID for the user")
    restaurant_id: str | None = Field(None, description="Unique ID for the restaurant")
    items: List[CartItem] = Field(..., description="List of all items currently in the cart")



class CartResponse(BaseModel):
    """Response model for a cart."""
    items: List[CartItem] = Field(..., description="List of all items currently in the cart")
