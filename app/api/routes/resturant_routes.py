from fastapi import APIRouter, Depends, status
from app.api.deps import get_resturant_service
from app.schemas.resturant_schema import ResturantResponse
from app.services.resturant_service import ResturantService

router = APIRouter(tags=["Resturant"])


@router.get(
    "/resturant",
    response_model=ResturantResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Resturant Check",
    description="Returns HTTP 200 and resturant information."
)
def check_resturant_status(
    service: ResturantService = Depends(get_resturant_service)
) -> ResturantResponse:
    """Check resturant status by delegating through service and repository layers."""
    return service.get_resturant_status()
