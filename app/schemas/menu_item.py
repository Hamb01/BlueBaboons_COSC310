from pydantic import BaseModel, Field


class MenuItem(BaseModel):
    id: str
    restaurant_id: str
    name: str
    description: str
    price: float = Field(ge=0)
    availability: bool
