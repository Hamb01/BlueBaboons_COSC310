from pydantic import BaseModel, Field

class RestaurantResponse(BaseModel):
    id: str = Field(..., description="Restaurant ID")
    name: str = Field(..., description="Restaurant name")
    location: str = Field(..., description="Restaurant location")
    isOpen: bool = Field(..., description="Restaurant open status")
    cuisine: str = Field(..., description="Restaurant's cuisine type")
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