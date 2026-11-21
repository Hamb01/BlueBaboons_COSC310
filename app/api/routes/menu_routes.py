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

from app.api.deps import get_current_user, get_menu_service
from app.schemas.menu_item import MenuItem, MenuResponse
from app.schemas.restaurant_schema import MenuItemRequest
from app.schemas.user_schema import User
from app.services.menu_service import MenuService

router = APIRouter(tags=["Menu"])


@router.put(
    "/restaurants/{restaurant_id}/menu/{item_id}",
    status_code=status.HTTP_200_OK,
        description=(
            "Replaces an existing menu item for the specified restaurant"
        ),
        responses={
            status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
            status.HTTP_403_FORBIDDEN: {"description": "Account has been deactivated"},
            status.HTTP_404_NOT_FOUND: {"description": "The restaurant or menu could not be found"},
            status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Data given was in the wrong form"}
        },
)
def replace_menu_item(
    restaurant_id: str,
    item_id: str,
    updated_data: dict,
    service: MenuService = Depends(get_menu_service),
    current_user: User = Depends(get_current_user)
):
    """Replace an existing menu item for the specified restaurant."""
    updated_item = service.update_menu_item(restaurant_id, item_id, updated_data, current_user=current_user)
    return MenuResponse(message="Menu item replaced successfully", item=updated_item)


@router.patch(
    "/restaurants/{restaurant_id}/menu/{item_id}",
    response_model=MenuItem,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
        status.HTTP_403_FORBIDDEN: {"description": "Owner or admin permission required"},
        status.HTTP_404_NOT_FOUND: {"description": "Restaurant or menu item not found"},
    },
)
def patch_menu_item(
    restaurant_id: str,
    item_id: str,
    updated_data: dict,
    service: MenuService = Depends(get_menu_service),
    current_user: User = Depends(get_current_user),
) -> MenuItem:
    """Partially update a menu item and return the updated item."""
    updated_item = service.update_menu_item(
        restaurant_id, item_id, updated_data, current_user=current_user
    )
    return MenuItem.model_validate(updated_item)


@router.post("/restaurants/{restaurant_id}/menu", status_code=status.HTTP_201_CREATED)
def add_menu_item(
    restaurant_id: str,
    payload: MenuItemRequest,
    service: MenuService = Depends(get_menu_service),
    current_user: User = Depends(get_current_user)
):
    """Add a menu item to the restaurant in the path."""
    item_data = payload.model_dump(exclude={"restaurant_id"})
    saved_item = service.add_new_menu_item(restaurant_id, item_data, current_user=current_user)
    return MenuResponse(message="Menu item created successfully", item=saved_item)


@router.get("/restaurants/{restaurant_id}/menu", 
    response_model=list[MenuItem],
    status_code=status.HTTP_200_OK,
        description=(
            "Return all menu items for a restaurant."
        ),
        responses={
            status.HTTP_404_NOT_FOUND: {"description": "The restaurant or menu could not be found"},
            status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Data given was in the wrong form"}
        },   
)
def get_menu(
    restaurant_id: str,
    service: MenuService = Depends(get_menu_service),
):
    """Return all menu items for a restaurant."""
    return service.get_menu(restaurant_id)


@router.get("/restaurants/{restaurant_id}/menu/{item_id}", 
    response_model=MenuItem,
    status_code=status.HTTP_200_OK,
        description=(
            "Return a specific menu item from one restaurant's menu."
        ),
        responses={
            status.HTTP_404_NOT_FOUND: {"description": "The restaurant or menu could not be found"}
        },  
)
def get_menu_item(
    restaurant_id: str,
    item_id: str,
    service: MenuService = Depends(get_menu_service),
):
    """Return a single menu item for a restaurant."""
    return service.get_menu_item(restaurant_id, item_id)


@router.delete(
    "/restaurants/{restaurant_id}/menu/{menu_item_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
        description=(
            "Delete a specific menu item from one restaurant's menu."
        ),
        responses={
            status.HTTP_404_NOT_FOUND: {"description": "The restaurant or menu could not be found"}
        },  
)
def remove_menu_item(
    restaurant_id: str,
    menu_item_id: str,
    service: MenuService = Depends(get_menu_service),
    current_user: User = Depends(get_current_user)
):
    """Delete the named menu item from the restaurant."""
    service.remove_menu_item(restaurant_id, menu_item_id, current_user=current_user)
