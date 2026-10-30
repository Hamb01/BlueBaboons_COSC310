from schemas.exception_schema import System_Error_Message

class DomainError(Exception, System_Error_Message):
    """Base exception for application domain errors."""
    

class RestaurantNotFoundError(DomainError):
    """Raised when a requested restaurant does not exist."""
    def __init__(self, restaurant_id: str):
        self.message = f"Restaurant with ID '{restaurant_id}' was not found."
    

class MenuItemNotFoundError(DomainError):
    """Raised when an item does not belong to the requested restaurant."""
    def __init__(self, restaurant_id: str, menu_id: str):
        self.message = f"Menu item '{menu_id}' does not exist inside restaurant '{restaurant_id}'."
            


class DataPersistenceError(DomainError):
    """Raised when reading or writing data persistence files encounters an error."""
    
    
