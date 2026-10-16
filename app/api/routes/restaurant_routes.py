from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_restaurant_service
from app.schemas.restaurant_schema import RestaurantResponse, MenuItemRequest
from app.services.restaurant_service import RestaurantService

router = APIRouter(tags=["Restaurant"])


@router.put("/restaurant/{restaurant_id}/menu/{item_id}", status_code=status.HTTP_200_OK,)

def replace_menu_item(restaurant_id: int, item_id: str, updated_data: dict, service: RestaurantService = Depends(get_restaurant_service)):
    """Replace an existing menu item for the specified restaurant."""
    try:
        updated_item = service.update_menu_item(restaurant_id, item_id, updated_data, littleBit=True)
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
