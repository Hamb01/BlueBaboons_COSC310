
"""Business logic for user authentication and authorization."""

from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserLogin
from app.core.exceptions import (
    AccountNotActiveError,
    UserAuthenticationError,
    UserNotFoundError,
)


class UserService:
    """Service layer containing business logic relating to the users of the system"""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def user_login(self, login_info : UserLogin):
        """
        user_login()
        -------------------
    
        Description:
            service to verify the login information provided by the user
    
        Args: 
            login_info : UserLogin -> username and password for the account (defined in pydantic model)
    
        Returns:
            token: A JSON web token for authenticating future requests.
    
        Raises: 
            UserAuthentificationError -> an incorrect username or password was entered
            DeactivatedAccountError   -> the user cannot login because an admin has deactivated their account
        """

        try:
            actual_user_data = self.repository.get_user_data(login_info.username)
        except UserNotFoundError as exc:
            raise UserAuthenticationError() from exc

        if login_info.password != actual_user_data.password:
            raise UserAuthenticationError()

        if not actual_user_data.account_is_active:
            raise AccountNotActiveError(
                actual_user_data.reason_for_deactivation or "Unspecified"
            )

        return self.repository.generate_web_token(actual_user_data.id)
