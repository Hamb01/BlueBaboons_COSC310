from enum import Enum

from pydantic import BaseModel

# Owner: Person A (customers + auth) — but agree on these shapes as a team first,
# because cart, orders, and the frontend all depend on them.


class UserRole(str, Enum):
    """Roles the backend authorizes against (the three roles named in the project spec)."""
    CUSTOMER = "customer"
    RESTAURANT_OWNER = "restaurant_owner"
    ADMIN = "admin"


class CurrentUser(BaseModel):
    """The authenticated user that every protected route receives from get_current_user."""
    # TODO: what is the minimum a route/service needs to know to make an authorization decision?
    # TODO: does a restaurant user need to carry which restaurant they manage?
    pass


############################################################################################
### Requests
############################################################################################

class CustomerRegister(BaseModel):
    # TODO: which fields does registering need? Which are required vs optional?
    # TODO: what validation belongs here (Pydantic) vs in the service (business rule)?
    pass


class LoginRequest(BaseModel):
    # TODO: what does a customer send to sign in?
    pass


class CustomerUpdate(BaseModel):
    # TODO: which profile fields may a customer change? How do you express "only update what was sent"?
    pass


class DeliveryAddressUpdate(BaseModel):
    # TODO: is an address one string or structured fields? What does checkout need from it?
    pass


############################################################################################
### Responses
############################################################################################

class TokenResponse(BaseModel):
    # TODO: what does the client need back after signing in to make authenticated requests?
    pass


class CustomerResponse(BaseModel):
    """Public view of a customer."""
    # TODO: which stored fields must NEVER be returned to the client?
    pass
