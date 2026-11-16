"""Schemas for Cart, cartItem, and cartResponse"""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Cart(BaseModel):
    """A single cart."""
    items: List[Dict[str, Any]] = Field(..., description="List of all items currently in the cart")

class cartItem(BaseModel):
    """A single item in a cart."""
    item_id: str = Field(..., description="Unique ID for the menu item")
    quantity: int = Field(..., description="The quantity of this item in the cart")
    
class CartResponse(BaseModel):
    """Response model for a cart."""
    items: List[Dict[str, Any]] = Field(..., description="List of all items currently in the cart")
