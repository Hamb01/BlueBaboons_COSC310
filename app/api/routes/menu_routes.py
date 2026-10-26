from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_menu_service
from app.services.menu_service import MenuService
from app.schemas.menu_item import MenuItem
from app.core.exceptions import RestaurantNotFoundError, MenuItemNotFoundError
from app.schemas.restaurant_schema import MenuItemRequest



#Coding Notes:
#Basic CRUD operations for menu items
#from top to bottom:

#replace menu item - replaces an existing menu item for the specified restaurant
#modify menu item - modifies an existing menu item for the specified restaurant
#add menu item - adds a new menu item to a specific restaurant based on the provided payload
#get menu - returns a list of menu items for a specific restaurant based on its ID
#get menu item - returns the details of a specific menu item based on its ID and the restaurant ID
#remove menu item - removes a specific menu item from a specific restaurant based on its ID and the restaurant ID


router = APIRouter(tags=["Menu"])


@router.put("/restaurant/{restaurant_id}/menu/{item_id}", status_code=status.HTTP_200_OK,)

def replace_menu_item(restaurant_id: int, item_id: str, updated_data: dict, service: MenuService = Depends(get_menu_service)):
    """Replace an existing menu item for the specified restaurant."""
    try:
        updated_item = service.update_menu_item(restaurant_id, item_id, updated_data)
        return {"message": "Menu item updated successfully", "item": updated_item}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/restaurant/{restaurant_id}/menu/{item_id}")
def modify_menu_item(restaurant_id: int, item_id: str, updated_data: dict, service: MenuService = Depends(get_menu_service)):
    """Modify an existing menu item for the specified restaurant."""
    try:
        updated_item = service.update_menu_item(restaurant_id, item_id, updated_data)
        return {"message": "Menu item updated successfully", "item": updated_item}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/restaurant/{restaurant_id}/menu", status_code=status.HTTP_201_CREATED)
def add_menu_item(payload: MenuItemRequest, service: MenuService = Depends(get_menu_service)):
    try:
        item_data = {
            "name": payload.name,
            "price": payload.price,
            "description": payload.description,
            "category": payload.category
        }

        saved_item = service.add_new_menu_item(payload.restaurant_id, item_data)
        return {"message": "Menu item added successfully", "item": saved_item}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/restaurants/{restaurant_id}/menu", response_model=list[MenuItem])
def get_menu(restaurant_id: str, service: MenuService = Depends(get_menu_service)):
    try:
        return service.get_menu(restaurant_id)
    except RestaurantNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/restaurants/{restaurant_id}/menu/{item_id}", response_model=MenuItem)
def get_menu_item(restaurant_id: str, item_id: str, service: MenuService = Depends(get_menu_service)):
    try:
        return service.get_menu_item(restaurant_id, item_id)
    except (RestaurantNotFoundError, MenuItemNotFoundError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete("/restaurants/{restaurant_id}/menu/{menu_item}", status_code = status.HTTP_204_NO_CONTENT)
def remove_menu_item(restaurant_id: str, menu_item_id: str, service: MenuService = Depends(get_menu_service)):
    service.remove_menu_item(restaurant_id, menu_item_id)
