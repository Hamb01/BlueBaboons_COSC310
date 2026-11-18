"""Tests for user services."""

import pytest

from app.core.exceptions import (
    AccountNotActiveError,
    BadDataInPersistenceLayerError,
    TokenBelongsToUnknownUserError,
    UserAuthenticationError,
    UserNotAuthorizedError,
    UserNotFoundError,
)
from app.schemas.user_schema import AccountStatusAndRole, Developer, UserLogin, CustomerResponse

def test_get_customer(isolated_user_service):
    """Test the ability to retrive customer data for a specific customer"""

    expected_data = {
        "c01" : {
            "username": "Charles",
            "wrong_data_form": "lol"
        },

        "c02" : {
            "id" : "c02",
            "username" : "harambe47",
            "name" : "Jane Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
            "hash_salt" : "7OAKfGhKVTqWecOn5H7t4Q==",

            "address" : "213-2532 Shoreline Dr",
            "city" : "Lake Country",
            "province" : "BC",
            "postal_code" : "V1V1V6",

            "account_is_active" : True,
            "balance" : 501.25
        },

        "c03" : {
            "id" : "c03",
            "username" : "superDuck47",
            "name" : "John Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
            "hash_salt" : "7OAKfGhKVTqWecOn5H7t4Q==",

            "address" : "213-2532 Shoreline Dr",
            "city" : "Lake Country",
            "province" : "BC",
            "postal_code" : "V1V1V6",

            "account_is_active" : False,
            "balance" : 501.25
        },

        "a01" : {
            "id" : "a01",
            "username" : "superDuck47",
            "name" : "John Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
            "hash_salt" : "7OAKfGhKVTqWecOn5H7t4Q==",
            "account_is_active" : True,

            "managed_restaurants" : ["r01"]
        }

    }
    isolated_user_service.repository.users = expected_data
    isolated_user_service.repository.save_to_file()

    deactivated_customer = isolated_user_service.repository.get_user_data_from_id("c03")
    active_customer = isolated_user_service.repository.get_user_data_from_id("c02")
    admin = isolated_user_service.repository.get_user_data_from_id("a01")

    response = isolated_user_service.get_customer("c02", active_customer)
    assert response.name == active_customer.name
    assert isinstance(response, CustomerResponse)
    second_response = isolated_user_service.get_customer("c02", admin)
    assert response == second_response
    with pytest.raises(UserNotAuthorizedError):
        isolated_user_service.get_customer("c03", active_customer)
    with pytest.raises(AccountNotActiveError):        
        isolated_user_service.get_customer("c03", deactivated_customer)


def test_deactivate_customer(isolated_user_service):
    """Test the ability to retrive customer data for a specific customer"""

    expected_data = {
        "c01" : {
            "username": "Charles",
            "wrong_data_form": "lol"
        },

        "c02" : {
            "id" : "c02",
            "username" : "harambe47",
            "name" : "Jane Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
            "hash_salt" : "7OAKfGhKVTqWecOn5H7t4Q==",

            "address" : "213-2532 Shoreline Dr",
            "city" : "Lake Country",
            "province" : "BC",
            "postal_code" : "V1V1V6",

            "account_is_active" : True,
            "balance" : 501.25
        },

        "c03" : {
            "id" : "c03",
            "username" : "superDuck47",
            "name" : "John Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
            "hash_salt" : "7OAKfGhKVTqWecOn5H7t4Q==",

            "address" : "213-2532 Shoreline Dr",
            "city" : "Lake Country",
            "province" : "BC",
            "postal_code" : "V1V1V6",

            "account_is_active" : False,
            "balance" : 501.25
        },

        "a01" : {
            "id" : "a01",
            "username" : "superDuck47",
            "name" : "John Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
            "hash_salt" : "7OAKfGhKVTqWecOn5H7t4Q==",
            "account_is_active" : True,

            "managed_restaurants" : ["r01"]
        },

        "d01" : {
            "id" : "d01",
            "username" : "superDuck47",
            "name" : "John Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
            "hash_salt" : "7OAKfGhKVTqWecOn5H7t4Q==",
            "account_is_active" : True

        }

    }
    isolated_user_service.repository.users = expected_data
    isolated_user_service.repository.save_to_file()

    deactivated_customer = isolated_user_service.repository.get_user_data_from_id("c03")
    active_customer = isolated_user_service.repository.get_user_data_from_id("c02")
    admin = isolated_user_service.repository.get_user_data_from_id("a01")
    developer = isolated_user_service.repository.get_user_data_from_id("d01")

    # test deactivating a user with corrupted data
    with pytest.raises(BadDataInPersistenceLayerError):
        isolated_user_service.deactivate_customer("c01", active_customer)

    # test deactivating user when your account is not active
    with pytest.raises(AccountNotActiveError):
        isolated_user_service.deactivate_customer("c02", deactivated_customer) # cannot deactivate an account if your account is not active

    # test a customer trying to deactivate someone else's account
    with pytest.raises(UserNotAuthorizedError):
        isolated_user_service.deactivate_customer("c03", active_customer) # cannot deactivate another user's account

    # test deactivating your own account
    isolated_user_service.deactivate_customer("c02", active_customer) 
    assert not isolated_user_service.repository.users["c02"]["account_is_active"]

    # test admin deactivating a customer's account
    isolated_user_service.repository.activate_user("c02")
    isolated_user_service.deactivate_customer("c02", admin) 
    assert not isolated_user_service.repository.users["c02"]["account_is_active"]

    # test a developer deactivating a customer's account
    isolated_user_service.repository.activate_user("c02")
    isolated_user_service.deactivate_customer("c02", developer)
    isolated_user_service.deactivate_customer("c02", developer) # verify that it still works if we are deactivating a deactivated account
    assert not isolated_user_service.repository.users["c02"]["account_is_active"]


