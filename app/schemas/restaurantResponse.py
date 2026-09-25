from pydantic import BaseModel, Field

from app.schemas.restaurant import Restaurant

class RestaurantResponse(Restaurant): #inherit from Restaurant schema
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "R12345",
                "name": "The Great Restaurant",
                "location": "123 Main St, City, Country",
                "isOpen": True,
                "cuisine": "Italian"
            }
        }
    }