from fastapi import APIRouter, Depends, status
from app.api.deps import get_health_service
from app.schemas.health import HealthResponse
from app.services.health_service import HealthService

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    description="Returns HTTP 200 indicating API and persistence layers are operational."
)
def check_health(
    service: HealthService = Depends(get_health_service)
) -> HealthResponse:
    """Check health status by delegating through service and repository layers."""
    return service.get_health_status()
