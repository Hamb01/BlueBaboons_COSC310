from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_restaurant_service
from app.services.restaurant_service import RestaurantService
from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from app.core.exceptions import RestaurantNotFoundError, MenuItemNotFoundError
from app.schemas.restaurant_schema import (
    RestaurantResponse,
    RestaurantCreate,
    RestaurantUpdate
)

router = APIRouter(tags=["Restaurant"])


MENU_WRITE_ERRORS = {
    404: {"description": "Restaurant or menu item not found"},
    500: {"description": "Menu data could not be saved"},
}


def _menu_write(operation):
    from app.core.exceptions import DataPersistenceError

    try:
        return operation()
    except (RestaurantNotFoundError, MenuItemNotFoundError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except DataPersistenceError as error:
        raise HTTPException(status_code=500, detail="Menu data could not be saved") from error


@router.post("/restaurants/{restaurant_id}/menu", response_model=MenuItem,
             status_code=201, responses=MENU_WRITE_ERRORS)
def add_menu_item(restaurant_id: str, payload: MenuItemCreate,
                  service: RestaurantService = Depends(get_restaurant_service)):
    """Add a menu item to an existing restaurant. The URL determines ownership."""
    return _menu_write(lambda: service.add_new_menu_item(restaurant_id, payload))


@router.put("/restaurants/{restaurant_id}/menu/{item_id}", response_model=MenuItem,
            responses=MENU_WRITE_ERRORS)
def replace_menu_item(restaurant_id: str, item_id: str, payload: MenuItemCreate,
                      service: RestaurantService = Depends(get_restaurant_service)):
    """Replace editable fields; preserve item ID and restaurant ownership."""
    return _menu_write(lambda: service.update_menu_item(restaurant_id, item_id, payload))


@router.patch("/restaurants/{restaurant_id}/menu/{item_id}", response_model=MenuItem,
              responses=MENU_WRITE_ERRORS)
def modify_menu_item(restaurant_id: str, item_id: str, payload: MenuItemUpdate,
                     service: RestaurantService = Depends(get_restaurant_service)):
    """Update only supplied fields, preserving omitted values and stable IDs."""
    return _menu_write(lambda: service.update_menu_item(restaurant_id, item_id, payload))


@router.get("/restaurant", response_model=RestaurantResponse)
def check_restaurant_status(
    service: RestaurantService = Depends(get_restaurant_service)
) -> RestaurantResponse:
    """Check restaurant status by delegating through service and repository layers."""
    return service.get_restaurant_status()


@router.get("/restaurants/{restaurant_id}/menu", response_model=list[MenuItem])
def get_menu(restaurant_id: str, service: RestaurantService = Depends(get_restaurant_service)):
    try:
        return service.get_menu(restaurant_id)
    except RestaurantNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/restaurants/{restaurant_id}/menu/{item_id}", response_model=MenuItem)
def get_menu_item(restaurant_id: str, item_id: str, service: RestaurantService = Depends(get_restaurant_service)):
    try:
        return service.get_menu_item(restaurant_id, item_id)
    except (RestaurantNotFoundError, MenuItemNotFoundError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

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
