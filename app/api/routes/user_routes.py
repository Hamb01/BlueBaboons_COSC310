"""API routes for user collection and detail operations """

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_user_service
from app.schemas.user_schema import UserLogin, Customer, Developer, SupportStaff
from app.services.user_service import UserService

router = APIRouter(tags=["Authentication"])

@router.post("/auth/login", status_code=status.HTTP_200_OK)
def user_login(login_info : UserLogin, service=get_user_service):
    """
    user_login()
    -------------------

    Description:
        http_endpoint to authenticate the user

    Args: 
        login_info : UserLogin -> username and password for the account (defined in pydantic model)

    Returns:
        token -> a json web token that can be passed along with future api requestes to verify that the user is authorized for those actions

    Raises: 
        UserAuthentificationError      -> an incorrect username or password was entered
        DeactivatedAccountError        -> the user cannot login because an admin has deactivated their account
        BadDataInPersistenceLayerError -> The data retrieved from the persistence layer had an error in it 
        ValidationEror                 -> the information passed was in an incorrect form
    """
    return service.user_login(login_info)