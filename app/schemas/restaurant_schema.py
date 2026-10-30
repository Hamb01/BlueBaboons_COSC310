from pydantic import BaseModel, Field
from typing import Optional


#Coding Notes:

#Schema is defined using Pydantic to model data for our application
#Optional is data fields that are not explicitly required for the schema to be valid.
#Restaurant Response is a Pydantic model that inherits from the restaurant schema and is used to validate the data returned from the service layer.
#The rest is pretty straight forward, the schema defines the data structure for the restaurant and menu item entities, including their fields and types. 
#The RestaurantResponse model includes an example of a valid restaurant object for documentation purposes.

class Restaurant(BaseModel):
    id: str = Field(..., description="Restaurant ID")
    name: str = Field(..., description="Restaurant name")
    location: str = Field(..., description="Restaurant location")
    isOpen: bool = Field(..., description="Restaurant open status")
    cuisine: str = Field(..., description="Restaurant cuisine type")
    opening_hours: str = Field(..., description="Restaurant opening hours")

class RestaurantCreate(BaseModel):
    name: str = Field(..., description="Restaurant name")
    location: str = Field(..., description="Restaurant location")
    isOpen: bool = Field(..., description="Restaurant open status")
    cuisine: str = Field(..., description="Restaurant cuisine type")
    opening_hours: str = Field(..., description="Restaurant opening hours")


class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Restaurant name")
    location: Optional[str] = Field(None, description="Restaurant location")
    isOpen: Optional[bool] = Field(None, description="Restaurant open status")
    cuisine: Optional[str] = Field(None, description="Restaurant cuisine type")
    opening_hours: Optional[str] = Field(None, description="Restaurant opening hours")

class MenuItemRequest(BaseModel):
    restaurant_id: int = Field(..., description="ID of the restaurant to which the menu item will be added")
    name: str = Field(..., description="Name of the menu item")
    price: float = Field(..., ge=0, description="Price of the menu item")
    description: str = Field(..., description="Description of the menu item")
    availability: bool = Field(True, description="Whether the item can be ordered (default true)")

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
