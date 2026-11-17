
"""Business logic for user authentication and authorization."""

from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import (
    AccountStatusAndRole,
    CustomerResponse,
    Customer,
    User,
    UserLogin
)
from app.core.exceptions import (
    AccountNotActiveError,
    InvalidRequestError,
    UserAuthenticationError,
    UserNotAuthorizedError,
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
            BadDataInPersistenceLayerError -> the data stored fo the user is malformed
            DeactivatedAccountError   -> the user cannot login because an admin has deactivated their account
        """

        try:
            actual_user_data = self.repository.get_user_data(login_info.username)
        except UserNotFoundError as exc:
            raise UserAuthenticationError() from exc

        if not self.repository.check_login_info(login_info, actual_user_data):
            raise UserAuthenticationError()

        if not actual_user_data.account_is_active:
            raise AccountNotActiveError(
                actual_user_data.reason_for_deactivation or "Unspecified"
            )

        return self.repository.generate_web_token(actual_user_data.id)

    def get_customer(self, id_to_get: str, current_user: User) -> CustomerResponse:
        """
        get_customer
        -------------------

        Description:
            retrives the information for the selected customer if the user is authorized

        Args: 
            id_to_get : string -> the id for the customer whose information you wish to retrieve
            current_user : user -> The data relaetd to the user who made the request

        Returns:
            CustomerResponse -> the information of the customer

        Raises: 
            DeactivatedAccountError -> The current users account is not active
            UserNotfoundError -> no such user is currently stored in the system
            UserNotAuthorizedError -> the current user cannot view the infomation of the customer (only active admins and the customer in question can request this data)
        """
        if not current_user.account_is_active:
            raise AccountNotActiveError(current_user.reason_for_deactivation)
        elif current_user.id == id_to_get or self.repository.verify_user_account(current_user.id) == AccountStatusAndRole.ACTIVE_RESTARUTANT_ADMIN:
            customer_data = self.repository.get_user_data_from_id(id_to_get)
        else:
            raise UserNotAuthorizedError

        if not isinstance(customer_data, Customer):
            raise InvalidRequestError("You cannot request non-customer data through the get-customer endpoint")

        response = CustomerResponse(
            username = customer_data.username,
            name = customer_data.name,
            email = customer_data.email,
            account_is_active = customer_data.account_is_active,
            
            address = customer_data.address,
            city = customer_data.city,
            province = customer_data.province,
            postal_code = customer_data.postal_code,
            
            balance = customer_data.balance
        )

        return response

        

