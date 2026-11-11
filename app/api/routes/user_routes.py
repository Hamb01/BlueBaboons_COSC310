"""API routes for user collection and detail operations """

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_user_service
from app.schemas.user_schema import User, Customer, Developer, SupportStaff
from app.services.user_service import UserService

router = APIRouter(tags=["Authentication"])

@router.post("/auth/login", status_code=status.HTTP_200_OK)
def user_login():
    """
    user_login()
    -------------------

    Description:
        http_endpoint to authenticate the user

    Args: 
        username : string -> their unique username
        password : string -> their unique password

    Returns:
        token -> a json web token that can be passed along with future api requestes to verify that the user is authorized for those actions

    Raises: 
        UserAuthentificationError -> an incorrect username or password was entered
        DeactivatedAccountError   -> the user cannot login because an admin has deactivated their account
        ValidationEror            -> the information passed was in an incorrect form
    """