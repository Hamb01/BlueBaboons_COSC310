"""Schemas for restaurant requests and responses."""

import re
from typing import Optional

from pydantic import AliasChoices, BaseModel, Field, field_validator

POSTAL_CODE_PATTERN = re.compile(r"^[A-Z]\d[A-Z] \d[A-Z]\d$")

# Coding Notes:
# Schema is defined using Pydantic to model data for our application.
# Optional fields are allowed for create/update requests.
# RestaurantResponse is used to validate data returned by the service layer.


class Restaurant(BaseModel):
    """Base restaurant model with the fields persisted for a restaurant."""

    address: str = Field(..., alias=AliasChoices("address", "Address"), description="Restaurant address")
    postal_code: str = Field(..., alias=AliasChoices("postal_code", "Postal_Code"), description="Restaurant postal code")
    id: str = Field(..., description="Restaurant ID")
    name: str = Field(..., description="Restaurant name")
    location: str = Field(..., description="Restaurant location")
    isOpen: bool = Field(..., description="Restaurant open status")
    cuisine: str = Field(..., description="Restaurant cuisine type")
    opening_hours: str = Field(..., description="Restaurant opening hours")

    @field_validator("address")
    @classmethod
    def address_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Address is required")
        return value

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, value: str) -> str:
        value = value.strip().upper()
        if not POSTAL_CODE_PATTERN.fullmatch(value):
            raise ValueError("Postal code must use the format A1A 1A1")
        return value


class RestaurantCreate(BaseModel):
    """Request schema for creating a restaurant."""

    address: str = Field(..., description="Restaurant address")
    postal_code: str = Field(..., description="Restaurant postal code")
    name: str = Field(..., description="Restaurant name")
    location: str = Field(..., description="Restaurant location")
    isOpen: bool = Field(..., description="Restaurant open status")
    cuisine: str = Field(..., description="Restaurant cuisine type")
    opening_hours: str = Field(..., description="Restaurant opening hours")

    @field_validator("address")
    @classmethod
    def address_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Address is required")
        return value

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, value: str) -> str:
        value = value.strip().upper()
        if not POSTAL_CODE_PATTERN.fullmatch(value):
            raise ValueError("Postal code must use the format A1A 1A1")
        return value


class RestaurantUpdate(BaseModel):
    """Partial update schema for restaurant fields."""

    address: Optional[str] = Field(None, description="Restaurant address")
    postal_code: Optional[str] = Field(None, description="Restaurant postal code")
    name: Optional[str] = Field(None, description="Restaurant name")
    location: Optional[str] = Field(None, description="Restaurant location")
    isOpen: Optional[bool] = Field(None, description="Restaurant open status")
    cuisine: Optional[str] = Field(None, description="Restaurant cuisine type")
    opening_hours: Optional[str] = Field(None, description="Restaurant opening hours")

    @field_validator("address")
    @classmethod
    def address_must_not_be_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Address is required")
        return value

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip().upper()
        if not POSTAL_CODE_PATTERN.fullmatch(value):
            raise ValueError("Postal code must use the format A1A 1A1")
        return value


class MenuItemRequest(BaseModel):
    """Request schema for a menu item added to a restaurant."""

    restaurant_id: int = Field(
        ...,
        description="ID of the restaurant to which the menu item will be added",
    )
    name: str = Field(..., description="Name of the menu item")
    price: float = Field(..., ge=0, description="Price of the menu item")
    description: str = Field(..., description="Description of the menu item")
    availability: bool = Field(True, description="Whether the item can be ordered")


class RestaurantResponse(Restaurant):
    """Validated restaurant response model used by the API."""

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "R12345",
                "name": "The Great Restaurant",
                "address": "123 Main St",
                "postal_code": "V1V 1V7",
                "location": "Kelowna",
                "isOpen": True,
                "cuisine": "Italian",
                "opening_hours": "09:00 - 22:00",
            }
        }
    }
