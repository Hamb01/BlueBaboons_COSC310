from pydantic import BaseModel, Field
from typing import Optional

class MenuItem(BaseModel):
    id: str
    restaurant_id: str
    name: str
    description: str
    price: float = Field(ge=0)
    availability: bool

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None,ge=0)
    availability: Optional[bool] = None
    