from fastapi import Depends
from app.repositories.resturant_repository import ResturantRepository
from app.services.resturant_service import ResturantService


def get_resturant_repository() -> ResturantRepository:
    """Dependency provider for ResturantRepository."""
    return ResturantRepository()


def get_resturant_service(
    repository: ResturantRepository = Depends(get_resturant_repository)
) -> ResturantService:
    """Dependency provider for ResturantService with injected repository."""
    return ResturantService(repository=repository)
