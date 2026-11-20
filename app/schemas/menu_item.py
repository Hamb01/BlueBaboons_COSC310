"""Menu item schema used when returning and validating menu entries."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MenuItem(BaseModel):
    """A single restaurant menu item."""

    id: str
    restaurant_id: str
    name: str
    description: str
    price: float = Field(ge=0)
    availability: bool


class MenuItemUpdate(BaseModel):
    """Request body for updating a menu item; only the fields sent are changed."""

    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(default=None, min_length=1, description="New name of the menu item")
    description: Optional[str] = Field(default=None, description="New description of the menu item")
    price: Optional[float] = Field(default=None, ge=0, description="New price; must not be negative")
    availability: Optional[bool] = Field(default=None, description="False marks the item as sold out")


class MenuItemWriteResponse(BaseModel):
    """Response returned after a menu item is added or updated."""

    message: str
    item: MenuItem
