from app.core.config import get_settings
from app.repositories.health_repository import HealthRepository
from app.schemas.health import HealthResponse


class HealthService:
    """Service layer coordinating application health and storage verification."""

    def __init__(self, repository: HealthRepository):
        self.repository = repository

    def get_health_status(self) -> HealthResponse:
        settings = get_settings()
        persistence_info = self.repository.check_persistence()

        return HealthResponse(
            status="ok",
            app_name=settings.app_name,
            version=settings.app_version,
            persistence=persistence_info["status"]
        )
