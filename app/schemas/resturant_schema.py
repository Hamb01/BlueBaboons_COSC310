from pydantic import BaseModel, Field


class ResturantResponse(BaseModel):
    id: str = Field(..., description="Resturant ID")
    name: str = Field(..., description="Resturant name")
    location: str = Field(..., description="Resturant location")
    isOpen: bool = Field(..., description="Resturant open status")
    cuisine: str = Field(..., description="Resturant cuisine type")

