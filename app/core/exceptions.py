"""Custom domain exceptions used across the application and API layer."""

#########################################################################################################################################
## 
## Each exception is defined as it's own class that will inherit from our
## base exception class "DomainError"
##
## Each Exception will contain the following:
## Status code -> which corresponds to a HTTP status code. THIS IS SET BY THE EXCEPTION HANDLER AND DOES NOT NEED TO BE MANUALLY ADDED
## Error message -> a Brief description of what went wrong (this is required)
## Additional Details -> Anything that you feel pertinent that didn't fit into the error message. This is an optional field
##
## All Exceptions will be automatically routed to the exception handler which will generate a response with the correct status code
## This step is no longewr needed in the routes layer (or elsewhere for that matter)
##
## The Exception Handlers can be found in main.py
##
#########################################################################################################################################


class DomainError(Exception):
    """Base exception for application domain errors."""

    def __init__(self):
        super().__init__()
        self.message = "Unknown error"
        self.details = "Exception never identified in exception handler"


class RestaurantNotFoundError(DomainError):
    """Raised when a requested restaurant does not exist."""

    def __init__(self, restaurant_id: str):
        super().__init__()
        self.message = f"Restaurant with ID {restaurant_id} was not found."
        self.details = ""


class MenuItemNotFoundError(DomainError):
    """Raised when an item does not belong to the requested restaurant."""

    def __init__(self, restaurant_id: str, menu_id: str):
        super().__init__()
        self.message = (
            f"Menu item {menu_id} does not exist inside restaurant {restaurant_id}."
        )
        self.details = ""


class EmptyMenuError(DomainError):
    """Raised when a restaurant has no menu items."""

    def __init__(self, restaurant_id: str, exists: bool = True):
        super().__init__()
        self.message = f"Restaurant with id {restaurant_id} has no menu"

        if exists:
            self.details = "Menu is empty"
        else:
            self.details = "Menu does not exist"


class DataPersistenceError(DomainError):
    """Raised when reading or writing persistence files encounters an error."""

    def __init__(self, file_name: str, access_type: str = ""):
        super().__init__()
        self.message = f"Failed to access file {file_name}"

        if access_type:
            self.details = f"{access_type} failed"
        else:
            self.details = ""
