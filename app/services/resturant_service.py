from app.core.config import get_settings
from app.repositories.resturant_repository import ResturantRepository
from app.schemas.resturant_schema import resturantResponse


class ResturantService:
    """Service layer coordinating application health and storage verification."""

    def __init__(self, repository: ResturantRepository):
        self.repository = repository

    def get_resturant_status(self) -> resturantResponse:
        information = self.repository.get_resturant_info();

        return resturantResponse(
            id = information.resturant_id,
            name = information.resturant_name,
            location = information .resturant_location,
            isOpen = information.resturant_isOpen,
            cuisine = information.resturant_cuisine
        )
