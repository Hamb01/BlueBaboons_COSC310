class DomainError(Exception):
    """Base exception for application domain errors."""
    pass


class RestaurantNotFoundError(DomainError):
    """Raised when a requested restaurant does not exist."""
    def __init__(self, restaurant_id: str):
        super().__init__(f"Restaurant with ID '{restaurant_id}' was not found.")
        self.restaurant_id = restaurant_id


class MenuItemNotFoundError(DomainError):
    """Raised when an item does not belong to the requested restaurant."""


class DataPersistenceError(DomainError):
    """Raised when reading or writing data persistence files encounters an error."""
    pass


# TODO (team): M2 needs domain errors for the failure cases below. Decide together:
#   - which exception classes you need (one per case? a few base classes?)
#   - which HTTP status code each one should become (401 vs 403? 404 vs 409 vs 422?)
#   - where that mapping lives, so routes don't each repeat try/except (see the TODO in app/main.py)
#
#   Failure cases to cover:
#     - customer / cart item / order does not exist
#     - missing or invalid credentials / token
#     - signed in, but the role is not allowed to do this
#     - deactivated customer tries to sign in, use a cart, or check out
#     - email already registered
#     - menu item unavailable or deactivated
#     - restaurant closed
#     - adding an item from a second restaurant to the cart
#     - invalid quantity
#     - checking out an empty cart
