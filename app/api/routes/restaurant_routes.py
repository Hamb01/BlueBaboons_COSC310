from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.deps import get_restaurant_service
from app.services.restaurant_service import RestaurantService
from app.core.exceptions import RestaurantNotFoundError
from app.schemas.restaurant_schema import (
    RestaurantResponse,
    RestaurantCreate,
    RestaurantUpdate
)



#Coding Notes:
#Basic CRUD operations for restaurants (menu item routes live in menu_routes.py)
#from top to bottom:

#list restaurants - returns a list of restaurants based on the search criteria
#get restaurant details - returns the details of a specific restaurant based on its ID
#create restaurant - creates a new restaurant based on the provided payload
#update restaurant - updates an existing restaurant based on the provided payload


#Each API endpoint and what they do:

#Get - Retrieves data from the master json
#put - Updates an existing restaurant based on the provided payload
#post - Creates a new restaurant based on the provided payload


router = APIRouter(tags=["Restaurant"])


@router.get(
    "/restaurants", response_model=list[RestaurantResponse], status_code=200,
    summary="List, search, and filter restaurants",
)
def list_restaurants(
    search: str | None = Query(None, description="Substring search name, cuisine, or location(ignore cases)"),
    cuisine: str | None = Query(None, description="Cuisine exact search(ignore cases)"),
    location: str | None = Query(None, description="Substring of location (ignores case)"),
    is_open: bool | None = Query(None, description="Filter by status"),
    service: RestaurantService = Depends(get_restaurant_service),
) -> list[RestaurantResponse]:
    return service.list_restaurants(search, cuisine, location, is_open)

@router.get(
    "/restaurants/{restaurant_id}",
    response_model=RestaurantResponse,
    status_code=status.HTTP_200_OK,
)
def get_restaurant_details(
    restaurant_id: str,
    service: RestaurantService = Depends(get_restaurant_service),
) -> RestaurantResponse:
    """Return restaurant details, or 404 for an unknown restaurant."""
    try:
        return service.get_restaurant_details(restaurant_id)
    except RestaurantNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post("/restaurants", status_code = status.HTTP_201_CREATED)
def create_restaurant(payload: RestaurantCreate, service: RestaurantService =
                      Depends(get_restaurant_service)):
    try:
        return service.create_restaurant(payload)
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))

@router.put("/restaurants/{restaurant_id}", status_code = status.HTTP_200_OK)
def update_restaurant(restaurant_id: str, payload: RestaurantUpdate, service:
    RestaurantService = Depends(get_restaurant_service)):

    try:
        return service.update_restaurant(restaurant_id, payload)
    except RestaurantNotFoundError as e:
        raise HTTPException(status_code = 404, detail = str(e))
    except Exception as e:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))
