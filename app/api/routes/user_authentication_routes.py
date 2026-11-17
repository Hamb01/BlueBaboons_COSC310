"""API routes for user collection and detail operations."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_user_service
from app.schemas.user_schema import UserLogin
from app.services.user_service import UserService

router = APIRouter(tags=["Authentication"])


@router.post("/auth/login", status_code=status.HTTP_200_OK)
def user_login(
    login_info: UserLogin,
    service: UserService = Depends(get_user_service),
):
    """
    user_login()
    -------------------

    Description:
        http_endpoint to authenticate the user

    Args:
        login_info : UserLogin -> username and password for the account
            (defined in pydantic model)

    Returns:
        token -> a json web token that can be passed along with future api
            requests to verify that the user is authorized for those actions

    Raises:
        UserAuthentificationError -> an incorrect username or password was entered
        AccountNotActiveError -> the user cannot login because an admin has
            deactivated their account
        BadDataInPersistenceLayerError -> the data retrieved from the
            persistence layer had an error in it
        ValidationEror -> the information passed was in an incorrect form
    """
    return service.user_login(login_info)
