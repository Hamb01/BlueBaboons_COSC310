from fastapi import APIRouter, Depends, HTTPException, Query, status
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


#Get resturant status
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

@router.post("/restaurant/{restaurant_id}/menu", 
             status_code=status.HTTP_201_CREATED, 
             summary="Add Menu Item", 
             description="Add a new menu item to the restaurant's menu."
)
def add_menu_item(payload: MenuItemRequest):
    try:
        item_data = {
            "name": payload.name,
            "price": payload.price,
            "description": payload.description,
            "category": payload.category
        }
        # Wired: Using the service instance
        saved_item = get_restaurant_service().add_new_menu_item(payload.restaurant_id, item_data)
        return {"message": "Menu item added successfully", "item": saved_item}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Modifying menu items
@router.patch("/restaurant/{restaurant_id}/menu/{item_id}", 
              status_code=status.HTTP_200_OK, 
              summary="Update Menu Item", 
              description="Update an existing menu item for the specified restaurant."
)
def modify_menu_item(restaurant_id: int, item_id: str, updated_data: dict, service: RestaurantService = Depends(get_restaurant_service)):
    """Modify an existing menu item for the specified restaurant."""
    try:
        updated_item = service.update_menu_item(restaurant_id, item_id, updated_data)
        return {"message": "Menu item updated successfully", "item": updated_item}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def replace_menu_item(restaurant_id: int, item_id: str, updated_data: dict, service: RestaurantService = Depends(get_restaurant_service)):
    """Replace an existing menu item for the specified restaurant."""
    try:
        updated_item = service.update_menu_item(restaurant_id, item_id, updated_data, littleBit=True)
        return {"message": "Menu item updated successfully", "item": updated_item}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/restaurant/{restaurant_id}/menu/{item_id}", status_code=status.HTTP_200_OK,)
  
def replace_menu_item_endpoint(restaurant_id: int, item_id: str, updated_data: dict, service: RestaurantService = Depends(get_restaurant_service)):
    """Endpoint to replace an existing menu item for the specified restaurant."""
    return replace_menu_item(restaurant_id, item_id, updated_data, service)


def run_validation_tests(
    restaurant_id: int,
    item_id: str,
    updated_data: dict,
):
    """Run validation tests for the update_menu_item function."""
    if updated_data is None or not isinstance(updated_data, dict):
        raise ValueError("Updated data must be a non-empty dictionary.")

    price = updated_data.get("price")
    if price is not None and (not isinstance(price, (int, float)) or price < 0):
        raise ValueError("Price must be a non-negative number.")

    if restaurant_id is None or item_id is None:
        raise ValueError("Restaurant ID and Item ID must be provided.")







