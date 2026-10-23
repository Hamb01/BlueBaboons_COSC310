from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """Roles the backend authorizes against."""
    CUSTOMER = "customer"
    RESTAURANT_OWNER = "restaurant_owner"
    ADMIN = "admin"


class CurrentUser(BaseModel):
    """The authenticated user, as returned by the get_current_user dependency.

    This is what every protected route receives. It deliberately holds only
    what authorization needs; services load the full record when they need more.
    """
    id: str = Field(..., description="User ID, e.g. 'u01'")
    role: UserRole
    restaurant_id: Optional[str] = Field(None, description="Restaurant a restaurant_owner manages")


############################################################################################
### Requests
############################################################################################

class CustomerRegister(BaseModel):
    name: str = Field(..., min_length=1, description="Customer's display name")
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="Login email (unique)")
    password: str = Field(..., min_length=8, description="Plain-text password; only a hash is stored")
    delivery_address: Optional[str] = Field(None, description="Default delivery address")


class LoginRequest(BaseModel):
    email: str = Field(..., description="Registered email")
    password: str = Field(..., description="Account password")


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="New display name")
    email: Optional[str] = Field(None, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="New login email")


class DeliveryAddressUpdate(BaseModel):
    delivery_address: str = Field(..., min_length=1, description="New default delivery address")


############################################################################################
### Responses
############################################################################################

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Send as 'Authorization: Bearer <token>'")
    token_type: str = "bearer"
    user_id: str
    role: UserRole


class CustomerResponse(BaseModel):
    """Public view of a customer. Never includes the password hash."""
    id: str
    name: str
    email: str
    role: UserRole = UserRole.CUSTOMER
    delivery_address: Optional[str] = None
    is_active: bool = True

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "u01",
                "name": "Sam Customer",
                "email": "sam@example.com",
                "role": "customer",
                "delivery_address": "1234 Lakeshore Rd, Kelowna",
                "is_active": True,
            }
        }
    }
