class DomainError(Exception):
    """Base exception for application domain errors."""
    pass


class RestaurantNotFoundError(DomainError):
    """Raised when a requested restaurant does not exist."""
    def __init__(self, restaurant_id: str):
        super().__init__(f"Restaurant with ID '{restaurant_id}' was not found.")
        self.restaurant_id = restaurant_id


class DataPersistenceError(DomainError):
    """Raised when reading or writing data persistence files encounters an error."""
    pass
