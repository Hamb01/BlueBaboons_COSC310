from fastapi import status


class DomainError(Exception):
    """Base exception for application domain errors.

    Every subclass carries the HTTP status code it maps to. The handler
    registered in app/main.py turns any DomainError into a JSON error
    response, so routes do not need their own try/except blocks.
    """
    status_code: int = status.HTTP_400_BAD_REQUEST


############################################################################################
### 404 - the requested resource does not exist
############################################################################################

class NotFoundError(DomainError):
    """Base class for errors raised when a requested resource does not exist."""
    status_code = status.HTTP_404_NOT_FOUND


class RestaurantNotFoundError(NotFoundError):
    """Raised when a requested restaurant does not exist."""
    def __init__(self, restaurant_id: str):
        super().__init__(f"Restaurant with ID '{restaurant_id}' was not found.")
        self.restaurant_id = restaurant_id


class MenuItemNotFoundError(NotFoundError):
    """Raised when an item does not belong to the requested restaurant."""


class CustomerNotFoundError(NotFoundError):
    """Raised when a requested customer account does not exist."""
    def __init__(self, customer_id: str):
        super().__init__(f"Customer with ID '{customer_id}' was not found.")
        self.customer_id = customer_id


class CartItemNotFoundError(NotFoundError):
    """Raised when updating or removing an item that is not in the cart."""
    def __init__(self, menu_item_id: str):
        super().__init__(f"Menu item '{menu_item_id}' is not in the cart.")
        self.menu_item_id = menu_item_id


class OrderNotFoundError(NotFoundError):
    """Raised when a requested order does not exist (or is not visible to the user)."""
    def __init__(self, order_id: str):
        super().__init__(f"Order with ID '{order_id}' was not found.")
        self.order_id = order_id


############################################################################################
### 401 / 403 - authentication and authorization
############################################################################################

class AuthenticationError(DomainError):
    """Raised when credentials or the bearer token are missing or invalid."""
    status_code = status.HTTP_401_UNAUTHORIZED


class PermissionDeniedError(DomainError):
    """Raised when an authenticated user's role does not allow the operation."""
    status_code = status.HTTP_403_FORBIDDEN


class InactiveAccountError(DomainError):
    """Raised when a deactivated customer tries to use their account."""
    status_code = status.HTTP_403_FORBIDDEN


############################################################################################
### 409 - the request is valid but conflicts with the current state
############################################################################################

class ConflictError(DomainError):
    """Base class for requests that are valid but conflict with current state."""
    status_code = status.HTTP_409_CONFLICT


class EmailAlreadyRegisteredError(ConflictError):
    """Raised when registering with an email that already has an account."""


class MenuItemUnavailableError(ConflictError):
    """Raised when a menu item is unavailable or deactivated."""


class RestaurantClosedError(ConflictError):
    """Raised when ordering from a restaurant that is not currently open."""


class MixedRestaurantCartError(ConflictError):
    """Raised when adding an item from a different restaurant than the cart's."""


class EmptyCartError(ConflictError):
    """Raised when checking out a cart that has no items."""


############################################################################################
### 422 - business-rule validation the request schema cannot express
############################################################################################

class InvalidQuantityError(DomainError):
    """Raised when a cart quantity is outside the allowed range."""
    status_code = 422


############################################################################################
### 500 - storage failures
############################################################################################

class DataPersistenceError(DomainError):
    """Raised when reading or writing data persistence files encounters an error."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
