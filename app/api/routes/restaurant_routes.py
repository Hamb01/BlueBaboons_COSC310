from fastapi import APIRouter, Depends, status
from app.api.deps import get_restaurant_service
from app.schemas.restaurant_schema import RestaurantResponse
from app.services.restaurant_service import RestaurantService

router = APIRouter(tags=["Restaurant"])


@router.get(
    "/restaurant",
    response_model=RestaurantResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Restaurant Check",
    description="Returns HTTP 200 and restaurant information."
)
def check_restaurant_status(
    service: RestaurantService = Depends(get_restaurant_service)
) -> RestaurantResponse:
    """Check restaurant status by delegating through service and repository layers."""
    return service.get_restaurant_status()
