from pydantic import BaseModel, Field
from typing import Optional

class Restaurant(BaseModel):
    id: str = Field(..., description="Restaurant ID")
    name: str = Field(..., description="Restaurant name")
    location: str = Field(..., description="Restaurant location")
    isOpen: bool = Field(..., description="Restaurant open status")
    cuisine: str = Field(..., description="Restaurant cuisine type")
    opening_hours: str = Field(..., description="Restaurant opening hours")
    


class RestaurantResponse(Restaurant): #inherit from Restaurant schema
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "R12345",
                "name": "The Great Restaurant",
                "location": "123 Main St, City, Country",
                "isOpen": True,
                "cuisine": "Italian",
                "opening_hours": "09:00 - 22:00"
            }
        }
    }