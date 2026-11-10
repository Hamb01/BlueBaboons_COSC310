"""Schemas for all types of users"""

from typing import Dict, List, str, Any, Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    """Base user model with the fields persisted for a user."""

    name: str = Field(..., description="First and Last name of the user")
    email: str = Field(..., description="Email that the user used while setting up account")
    password: str = Field(..., description="Password used by the user to sign in")
    account_is_active: bool = Field(..., description="boolean to reflect if the account is currently allowed to interact with the system")


class Customer(User):
    """Class to hold the account information of paying customers who interact with our system"""

    address: str = Field(..., description="street address of the user")
    city: str = Field(..., description="The city that the user lives in")
    province: str = Field(..., description="the Province that the user lives in")
    postal_code: str = Field(..., description="Postal conde for the users primary address")

    balance: float = Field(..., description="In store credit that the customer may use to pay for orders")
    order_history: Optional[Dict[str, Any]] = Field(..., description="Dictionary of all previous orders made by this customer")
    cart: Optional[Dict[str, Any]] = Field(..., description="Dictionary of all items currently in the cart")

class RestaurantAdmin(User):
    """Class to hold the account information of people who can create, edit and delete restaurants and their information"""

    managed_restaurants: List[str] = Field(..., description="the Ids of the restaurant that they have permission to edit")

class Developer(User):
    """Class to hold the account information for code developers. They are at the top of the hierarchy and can edit anything in the system"""

class SupportStaff(User):
    """Class to hold the account information for the workers who will actually make and deliver orders"""
