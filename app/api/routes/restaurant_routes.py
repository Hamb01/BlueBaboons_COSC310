from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_restaurant_service
from app.services.restaurant_service import RestaurantService
from app.schemas.menu_item import MenuItem
from app.core.exceptions import RestaurantNotFoundError, MenuItemNotFoundError
from app.schemas.restaurant_schema import (
    RestaurantResponse,
    MenuItemRequest,
    RestaurantCreate,
    RestaurantUpdate
)

router = APIRouter(tags=["Restaurant"])


@router.put("/restaurant/{restaurant_id}/menu/{item_id}", status_code=status.HTTP_200_OK,)

def replace_menu_item(restaurant_id: int, item_id: str, updated_data: dict, service: RestaurantService = Depends(get_restaurant_service)):
    """Replace an existing menu item for the specified restaurant."""
    try:
        updated_item = service.update_menu_item(restaurant_id, item_id, updated_data)
        return {"message": "Menu item updated successfully", "item": updated_item}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/restaurant/{restaurant_id}/menu/{item_id}")
def modify_menu_item(restaurant_id: int, item_id: str, updated_data: dict, service: RestaurantService = Depends(get_restaurant_service)):
    """Modify an existing menu item for the specified restaurant."""
    try:
        updated_item = service.update_menu_item(restaurant_id, item_id, updated_data)
        return {"message": "Menu item updated successfully", "item": updated_item}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/restaurant/{restaurant_id}/menu", status_code=status.HTTP_201_CREATED)
def add_menu_item(payload: MenuItemRequest):
    try:
        item_data = {
            "name": payload.name,
            "price": payload.price,
            "description": payload.description,
            "category": payload.category
        }

        saved_item = get_restaurant_service().add_new_menu_item(payload.restaurant_id, item_data)
        return {"message": "Menu item added successfully", "item": saved_item}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

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

@router.delete("/restaurants/{restaurant_id}/menu/{menu_item}", status_code = status.HTTP_204_NO_CONTENT)
def remove_menu_item(restaurant_id: str, menu_item_id: str, service: RestaurantService = Depends(get_restaurant_service)):
    service.remove_menu_item(restaurant_id, menu_item_id)