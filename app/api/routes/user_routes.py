"""API routes for user collection and detail operations."""

from fastapi import APIRouter, Depends, responses, status

from app.api.deps import (get_current_active_customer, get_current_active_user, get_current_user, get_user_service)
from app.schemas.user_schema import (
    Customer, 
    CustomerCreate,
    CustomerResponse, 
    CustomerUpdate, 
    User,
    UserCreate,
    UserResponse
)
from app.services.user_service import UserService

router = APIRouter(tags=["Users"])

@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
        description="used to create a new user account",
        responses={
            status.HTTP_409_CONFLICT: {"description": "The username is already in use"},
            status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "error in input data"},
        },
)
def register_user(new_user: UserCreate,service = Depends(get_user_service)):
    """create a new user account and add it to the system"""
    return service.create_new_user(new_user)