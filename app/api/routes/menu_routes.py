"""API routes for restaurant menu item CRUD operations."""

# Coding Notes:
# Basic CRUD operations for menu items.
# From top to bottom:
# - replace menu item
# - modify menu item
# - add menu item
# - get menu
# - get menu item
# - remove menu item
#
# Each API endpoint and what they do:
# - PUT replaces an existing menu item for the specified restaurant
# - PATCH modifies an existing menu item for the specified restaurant
# - POST adds a new menu item to a specific restaurant based on the provided payload
# - GET returns menu data for a restaurant or a single menu item
# - DELETE removes a specified menu item from the restaurant

from fastapi import APIRouter, Depends, status

from app.api.deps import get_menu_service
from app.schemas.menu_item import MenuItem
from app.schemas.restaurant_schema import MenuItemRequest
from app.services.menu_service import MenuService

router = APIRouter(tags=["Menu"])


def validation_detail(error: ValidationError) -> list:
    """Shape a service-level ValidationError like FastAPI's own 422 response."""
    return error.errors(include_url=False, include_context=False, include_input=False)


@router.put(
    "/restaurant/{restaurant_id}/menu/{item_id}", 
    status_code=status.HTTP_200_OK,)

def replace_menu_item(restaurant_id: str, item_id: str, updated_data: dict, service: MenuService = Depends(get_menu_service)):
    """Replace an existing menu item for the specified restaurant."""
    updated_item = service.update_menu_item(restaurant_id, item_id, updated_data)
    return {"message": "Menu item updated successfully", "item": updated_item}


@router.patch("/restaurant/{restaurant_id}/menu/{item_id}")
def modify_menu_item(
    restaurant_id: str, 
    item_id: str, 
    updated_data: dict, 
    service: MenuService = Depends(get_menu_service)):
    """Modify an existing menu item for the specified restaurant."""
    updated_item = service.update_menu_item(restaurant_id, item_id, updated_data)
    return {"message": "Menu item updated successfully", "item": updated_item}


@router.post("/restaurant/{restaurant_id}/menu", status_code=status.HTTP_201_CREATED)
def add_menu_item(
    restaurant_id: str,
    payload: MenuItemRequest,
    service: MenuService = Depends(get_menu_service),
):
    """Add a menu item to the restaurant in the path."""
    item_data = payload.model_dump(exclude={"restaurant_id"})
    saved_item = service.add_new_menu_item(restaurant_id, item_data)
    return {"message": "Menu item added successfully", "item": saved_item}


@router.get("/restaurants/{restaurant_id}/menu", response_model=list[MenuItem])
def get_menu(
    restaurant_id: str,
    service: MenuService = Depends(get_menu_service),
):
    """Return all menu items for a restaurant."""
    return service.get_menu(restaurant_id)


@router.get("/restaurants/{restaurant_id}/menu/{item_id}", response_model=MenuItem)
def get_menu_item(
    restaurant_id: str,
    item_id: str,
    service: MenuService = Depends(get_menu_service),
):
    """Return a single menu item for a restaurant."""
    return service.get_menu_item(restaurant_id, item_id)


@router.delete(
    "/restaurants/{restaurant_id}/menu/{menu_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_menu_item(
    restaurant_id: str,
    menu_item_id: str,
    service: MenuService = Depends(get_menu_service),
):
    """Delete the named menu item from the restaurant."""
    service.remove_menu_item(restaurant_id, menu_item_id)
