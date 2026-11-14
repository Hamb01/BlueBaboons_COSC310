"""Schemas for all types of users"""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class User(BaseModel):
    """Base user model with the fields persisted for a user."""

    id: str = Field(..., description="unique Id for the user")
    username: str = Field(..., description="username for the account")
    name: str = Field(..., description="First and Last name of the user")
    email: str = Field(..., description="Email that the user used while setting up account")
    password: str = Field(..., description="Password used by the user to sign in")
    account_is_active: bool = Field(..., description="boolean to reflect if the account is currently allowed to interact with the system")
    reason_for_deactivation: Optional[str] = Field(default=None, description="Brief explanation of why the users access to the system was revoked")


class Customer(User):
    """Class to hold the account information of paying customers who interact with our system"""

    address: str = Field(..., description="street address of the user")
    city: str = Field(..., description="The city that the user lives in")
    province: str = Field(..., description="the Province that the user lives in")
    postal_code: str = Field(..., description="Postal conde for the users primary address")

    balance: float = Field(..., description="In store credit that the customer may use to pay for orders")
    order_history: Optional[Dict[str, Any]] = Field(default=None, description="Dictionary of all previous orders made by this customer")
    cart: Optional[Dict[str, Any]] = Field(default=None, description="Dictionary of all items currently in the cart")

class RestaurantOwner(User):
    """Class to hold the account information of people who create, edit and delete restaurants"""

    owned_restaurants: List[str] = Field(..., description="the Ids of the restaurant that they own")

class RestaurantAdmin(User):
    """Class to hold the account information of people who can edit restaurant information"""

    managed_restaurants: List[str] = Field(..., description="the Ids of the restaurant that they have permission to edit")

class Developer(User):
    """Class to hold the account information for code developers. They are at the top of the hierarchy and can edit anything in the system"""

class SupportStaff(User):
    """Class to hold the account information for the workers who will actually make and deliver orders"""

class UserLogin(BaseModel):
    """Pydantic model to define the request body for logging into an account"""

    username: str = Field(..., description="Unique user name associated with the user")
    password: int | float | str = Field(..., description="Password associated with the user") # allowing many types because we will ensure it matches later

class AccountStatusAndRole(Enum):
    """Enumeration to capture the current status of a persons account as well as their current role"""
    ACTIVE_CUSTOMER = 1
    DEACTIVATED_CUSTOMER = 2
    ACTIVE_RESTAURANT_OWNER = 3
    DEACTIVATED_RESTAURANT_OWNER = 4
    ACTIVE_RESTARUTANT_ADMIN = 5
    DEACTIVATED_RESTAURANT_ADMIN = 6
    ACTIVE_DEVELOPER = 7
    DEACTIVATED_DEVELLOPER = 8
    ACTIVE_SUPPORT_STAFF = 9
    DEACTIVATED_SUPPORT_STAFF = 10