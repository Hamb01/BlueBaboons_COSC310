
"""Business logic for user authentication and authorization."""

from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import (
    AccountStatusAndRole,
    CustomerResponse,
    CustomerUpdate,
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

    def user_login(self, login_info: UserLogin):
        """
        user_login()
        -------------------

        Description:
            service to verify the login information provided by the user

        Args:
            login_info : UserLogin -> username and password for the account
                (defined in pydantic model)

        Returns:
            token: A JSON web token for authenticating future requests.

        Raises:
            UserAuthentificationError -> an incorrect username or password was entered
            BadDataInPersistenceLayerError -> the data stored fo the user is malformed
            AccountNotActiveError   -> the user cannot login because their account has been deactivated
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

    def update_customer(
        self, id_to_update: str, updated_data: CustomerUpdate, current_user: User
    ) -> CustomerResponse:
        """
        update_customer
        -------------------

        Description:
            updates the information for the selected customer if the user is authorized.
            Only the fields that were sent in the request are changed.

        Args:
            id_to_update : string -> the id of the customer to update
            updated_data : CustomerUpdate -> the fields to change
            current_user : User -> the user who made the request

        Returns:
            CustomerResponse -> the customer's information after the update

        Raises:
            AccountNotActiveError -> the current user's account is not active
            UserNotAuthorizedError -> a customer can only update their own information
            InvalidRequestError -> the id does not belong to a customer
        """
        # Deactivated accounts cannot change anything.
        if not current_user.account_is_active:
            raise AccountNotActiveError(current_user.reason_for_deactivation)

        # A customer may only edit their own information.
        if current_user.id != id_to_update:
            raise UserNotAuthorizedError

        # Make sure the id belongs to a customer (ids starting with 'c'),
        # since only customers have address/city/province/postal_code fields.
        customer_data = self.repository.get_user_data_from_id(id_to_update)
        if not isinstance(customer_data, Customer):
            raise InvalidRequestError(
                "You cannot update non-customer data through the update-customer endpoint"
            )

        changes = updated_data.model_dump(exclude_unset=True)

        if changes:
            self.repository.users[id_to_update].update(changes)
            self.repository.save_to_file()
        # An empty body means nothing changed, so we skip the disk write.

        # Re-read the customer so the response reflects what is now stored,
        # then strip it down to the public fields before returning it.
        return self._to_customer_response(
            self.repository.get_user_data_from_id(id_to_update)
        )

    @staticmethod
    def _to_customer_response(customer_data: Customer) -> CustomerResponse:
        """
        _to_customer_response
        -------------------

        Description:
            Converts a stored Customer into the CustomerResponse that is sent
            back to the client. Shared by get_customer and update_customer so
            both endpoints return exactly the same shape.

            A Customer holds private fields (password, hash_salt, cart,
            order_history, ...). Copying across ONLY the public fields below
            means those private fields can never leak into an API response.
            If CustomerResponse gains a new field, add it here once and both
            endpoints pick it up.

            It is a @staticmethod because it doesn't use self; it just turns
            one model into another.

        Args:
            customer_data : Customer -> the full customer record from the repository

        Returns:
            CustomerResponse -> the public view of the customer
        """
        return CustomerResponse(
            username=customer_data.username,
            name=customer_data.name,
            email=customer_data.email,
            account_is_active=customer_data.account_is_active,
            address=customer_data.address,
            city=customer_data.city,
            province=customer_data.province,
            postal_code=customer_data.postal_code,
            balance=customer_data.balance,
        )

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
            AccountNotActiveError -> The current users account is not active
            UserNotfoundError -> no such user is currently stored in the system
            UserNotAuthorizedError -> the current user cannot view the information
                of the customer (only active admins and the customer in question
                can request this data)
            BadDataInPersistenceLayerError -> the stored data is in the wrong form
        """
        if not current_user.account_is_active:
            raise AccountNotActiveError(current_user.reason_for_deactivation)

        if current_user.id == id_to_get or (
            self.get_account_status_and_role(current_user.id) in (AccountStatusAndRole.ACTIVE_RESTAURANT_ADMIN, AccountStatusAndRole.ACTIVE_DEVELOPER)
        ):
            customer_data = self.repository.get_user_data_from_id(id_to_get)
        else:
            raise UserNotAuthorizedError("view customer information")

        if not isinstance(customer_data, Customer):
            raise InvalidRequestError(
                "You cannot request non-customer data through the get-customer "
                "endpoint"
            )
            
        return self._to_customer_response(customer_data)

    def deactivate_customer(self, id_to_deactivate: str, current_user: User, reason_for_deactivation: str = ""):
        """
        deactivate_customer
        -------------------

        Description:
            method to allow for the deactivationg of a customers account

        Args: 
            id_to_deactivate : string -> the id for the customer who you wish to deactivate
            current_user : user -> The data relaetd to the user who made the request
            reason_to_deactivate : string -> optional description of why you wish to delete your account

        Returns:
            void

        Raises: 
            AccountNotActiveError -> the current user's account has been deactivated
            UserNotAuthorizedError -> the current user is not allowed to do this action
            UserNotFoundError -> no such userr is stored in the system
            BadDataInPersistenceLayerError -> something went wrong while accessing the data related to the user
            DataPersistenceError -> an error occured while saving the changes done to the user
        """
        if not current_user.account_is_active:
            raise AccountNotActiveError(current_user.reason_for_deactivation)
        if not self.get_account_status_and_role(id_to_deactivate) in (AccountStatusAndRole.ACTIVE_CUSTOMER, AccountStatusAndRole.DEACTIVATED_CUSTOMER):
            raise InvalidRequestError("Cannot remove user through cusomer endpoint")
        if current_user.id == id_to_deactivate:
            self.repository.deactivate_user(id_to_deactivate, reason_for_deactivation)
        elif self.get_account_status_and_role(current_user.id) in (AccountStatusAndRole.ACTIVE_RESTAURANT_OWNER, 
                                                                      AccountStatusAndRole.ACTIVE_RESTAURANT_ADMIN, 
                                                                      AccountStatusAndRole.ACTIVE_DEVELOPER):
            self.repository.deactivate_user(id_to_deactivate, reason_for_deactivation)
        else:
            raise UserNotAuthorizedError("deactivate customer")

    def require_active(self, user_id: str) -> bool:
        """
        require_active
        -------------------

        Description:
            checks to see if a particular user's account is active. Meant to be used to limit the abilities of deactivated accounts

        Args: 
            user_id : string -> the unique id of the user that you need to be active

        Returns:
            bool -> true if the user is active 
            (mute point since this function will throw an exception otherwise, but this means that it can be used in a conditioal expression)

        Raises: 
            UserAuthentificationError -> an incorrect username or password was entered
            BadDataInPersistenceLayerError -> the data stored fo the user is malformed
            AccountNotActiveError   -> the user's account has been deactivated
        """

        userdata = self.repository.get_user_data_from_id(user_id)

        if not userdata.account_is_active:
            raise AccountNotActiveError(userdata.reason_for_deactivation or "Unspecified")

        return True

    def get_account_status_and_role(self, user_id: str) -> AccountStatusAndRole :
        """
        get_account_status_and_role
        ----------------------------

        Description:
            returns an enumeration representing the user's current account status and their role

        Args: 
            user_id : string -> unique identifier belonging to the user you wish to look up

        Returns:
            AccountStatusAndRole -> Enumeration that tells us a user's role and if their account is active

        Raises: 
            BadDataInPersistenceLayerError -> get_user_data_from_id returned the wrong type
            UserNotFoundError -> No such user exists in our system
        """
        return self.repository.verify_user_account(user_id)
