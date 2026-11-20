"""API routes for user collection and detail operations."""

from fastapi import APIRouter, Depends, responses, status

from app.api.deps import (get_current_active_customer, get_current_active_user, get_current_user, get_user_service)
from app.schemas.user_schema import Customer, CustomerResponse, CustomerUpdate, User
from app.services.user_service import UserService

router = APIRouter(tags=["Customers"])



@router.patch(
    "/customers/me",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
       description=(
            "Updates the authenticated customer's information. Only fields that are "
            "provided in the request body will be updated; all other fields remain "
            "unchanged."
       ),
        responses={
            status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
            status.HTTP_403_FORBIDDEN: {"description": "Account has been deactivated"},
            status.HTTP_422_UNPROCESSABLE_CONTENT: {
                "description": "Invalid body, e.g. invalid address"
            },
        },
)
def update_customer_me(
    updated_data: CustomerUpdate,
    current_user: Customer = Depends(get_current_active_customer),
    service: UserService = Depends(get_user_service),
)-> CustomerResponse:
    """
    update_customer_me
    -------------------

    Description:
        updates the information related to the customer with the specified ID

    Args:
        none

    Returns:
        CustomerResponse -> Information related to the specified customer
            (minus anything that is not readable, not user editable or meant to
            be accessed via another endpoint)

    Raises:
        UserAuthentificationError -> an incorrect username or password was entered
        UserNotAuthorizedError -> User does not have permission to fetch the data
        UserNotFoundError -> No such user could be found in the system
        AccountNotActiveError -> the user cannot login because an admin has
                deactivated their account
    """
    return service.update_customer(current_user.id, updated_data, current_user)

@router.get(
    "/customers/me",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
        description=(
            "Retrives the information for the current customer"
        ),
        responses={
            status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
            status.HTTP_403_FORBIDDEN: {"description": "Account has been deactivated"},
            status.HTTP_422_UNPROCESSABLE_CONTENT: {
                "description": "Invalid body, e.g. invalid address"
            },
        },
)
def get_customer_me(
    current_user: Customer = Depends(get_current_active_customer),
    service: UserService = Depends(get_user_service),
):
    """
    get_customer
    -------------------

    Description:
        returns the information related to the customer with the specified ID

    Args:
        customer_id : string -> the id belonging to the specific customer you
            wish to get the data for

    Returns:
        CustomerResponse -> Information related to the specified customer
            (minus anything that is not readable, not user editable or meant to
            be accessed via another endpoint)

    Raises:
        UserAuthentificationError -> an incorrect username or password was entered
        UserNotAuthorizedError -> User does not have permission to fetch the data
        UserNotFoundError -> No such user could be found in the system
        AccountNotActiveError -> the user cannot login because an admin has
            deactivated their account
    """
    return service.get_customer(current_user.id, current_user)

@router.get(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
        description=(
            "Retrives the information for a specific customer"
        ),
        responses={
            status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
            status.HTTP_403_FORBIDDEN: {"description": "Account has been deactivated or User is not authorized"},
            status.HTTP_422_UNPROCESSABLE_CONTENT: {
                "description": "Invalid body, e.g. invalid address"
            },
        },
)
def get_customer(
    customer_id: str,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
):
    """
    get_customer
    -------------------

    Description:
        returns the information related to the customer with the specified ID

    Args:
        customer_id : string -> the id belonging to the specific customer you
            wish to get the data for

    Returns:
        CustomerResponse -> Information related to the specified customer
    """
    return service.get_customer(customer_id, current_user)

@router.post(
    "/customers/me/deactivate",
    response_model=None,
    status_code=status.HTTP_200_OK,
        description=(
            "Retrives the information for a specific customer"
        ),
        responses={
            status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
            status.HTTP_403_FORBIDDEN: {"description": "Account has been deactivated"},
        },
)
def deactivate_my_customer_account(current_user = Depends(get_current_user), service = Depends(get_user_service), reason_for_deactivation: str = ""):
    """
    deactivate_my_customer_account
    ------------------------------

    Description:
        endpoint to allow for the deactivationg of a customers own account

    Args: 
        current_user : user -> The data relaetd to the user who made the request
        reason_for_activation : string -> optional description for why you wish to deactivate your account

    Returns:
        void

    Raises: 
        AccountNotActiveError -> the current user's account has been deactivated
        UserNotAuthorizedError -> the current user is not allowed to do this action
        UserNotFoundError -> no such userr is stored in the system
        BadDataInPersistenceLayerError -> something went wrong while accessing the data related to the user
        DataPersistenceError -> an error occured while saving the changes done to the user
    """
    service.deactivate_customer(current_user.id, current_user, reason_for_deactivation)

@router.post(
    "/customers/{customer_id}/deactivate",
    response_model=None,
    status_code=status.HTTP_200_OK,
        description=(
            "Retrives the information for a specific customer"
        ),
        responses={
            status.HTTP_401_UNAUTHORIZED: {"description": "Missing or invalid token"},
            status.HTTP_403_FORBIDDEN: {"description": "Account has been deactivated"},
        },
)
def deactivate_customer_account(customer_id: str, current_user = Depends(get_current_user), service = Depends(get_user_service), reason_for_deactivation: str = ""):
    """
    deactivate_customer_account
    ------------------------------

    Description:
        endpoint to allow for the deactivationg of a specific customer's account

    Args: 
        customer_id : string -> the id for the customer who you wish to deactivate
        current_user : user -> The data relaetd to the user who made the request
        reason_for_activation : string -> optional description for why you wish to deactivate your account

    Returns:
        void

    Raises: 
        AccountNotActiveError -> the current user's account has been deactivated
        UserNotAuthorizedError -> the current user is not allowed to do this action
        UserNotFoundError -> no such userr is stored in the system
        BadDataInPersistenceLayerError -> something went wrong while accessing the data related to the user
        DataPersistenceError -> an error occured while saving the changes done to the user
    """
    service.deactivate_customer(customer_id, current_user, reason_for_deactivation)

