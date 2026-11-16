"""Menu item schema used when returning and validating menu entries."""

from pydantic import BaseModel, Field


class MenuItem(BaseModel):
    """A single restaurant menu item."""

    id: str
    restaurant_id: str
    name: str
    description: str
    price: float = Field(ge=0)
    availability: bool
