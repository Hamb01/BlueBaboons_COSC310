from pydantic import BaseModel, Field

class RestaurantResponse(BaseModel):
    id: str = Field(..., description="Restaurant ID")
    name: str = Field(..., description="Restaurant name")
    location: str = Field(..., description="Restaurant location")
    isOpen: bool = Field(..., description="Restaurant open status")
    cuisine: str = Field(..., description="Restaurant cuisine type")


class MenuItemRequest(BaseModel):
    restaurant_id: int = Field(..., description="ID of the restaurant to which the menu item will be added")
    name: str = Field(..., description="Name of the menu item")
    price: float = Field(..., description="Price of the menu item")
    description: str = Field(..., description="Description of the menu item")
    category: str = Field(..., description="Category of the menu item")