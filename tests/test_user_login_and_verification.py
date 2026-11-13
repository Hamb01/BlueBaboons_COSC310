import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user_schema import (
    UserLogin, 
    User, 
    Customer, 
    RestaurantOwner, 
    RestaurantAdmin, 
    Developer, 
    SupportStaff, 
    AccountStatusAndRole
    )
from app.core.exceptions import (
    UserNotFoundError, 
    BadDataInPersistenceLayerError, 
    TokenBelongsToUnknownUserError, 
    UserAuthenticationError, 
    AccountNotActiveError
    )

def test_format_of_all_user_data(isolated_user_repo):
    """Checks through Users.json to verify that all of our data folows the forms in the schemas"""

    for id, data in isolated_user_repo.users.items():
        assert data == isolated_user_repo.get_user_data_from_id(id).model_dump(exclude_none=True)
    


#################################################################################################################################################
## Test User Authentication related functions in Repository Layer
#################################################################################################################################################

def test_get_user_data_by_username(isolated_user_repo):
    """Tests if we can retrieve the correct user from the persistence layer. Also tests saving data to persistence layer in the process"""

    expected_data = {
        "c01" : {
            "username": "Charles",
            "wrong_data_form": "lol"
        },

        "d02" : {
            "id" : "d02",
            "username" : "harambe47",
            "name" : "Jane Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "superHardPassword1234",

            "address" : "213-2532 Shoreline Dr",
            "city" : "Lake Country",
            "province" : "BC",
            "postal_code" : "V1V1V6",

            "account_is_active" : True,
            "balance" : 501.25
        }
    }
    isolated_user_repo.users = expected_data
    isolated_user_repo.save_to_file()
    retrieved_data = isolated_user_repo.get_user_data("harambe47")
    assert retrieved_data.name == expected_data["d02"]["name"]
    assert isinstance(retrieved_data, Developer)
    with pytest.raises(UserNotFoundError):
        retrieved_data = isolated_user_repo.get_user_data("james42")
    with pytest.raises(BadDataInPersistenceLayerError):
        retrieved_data = isolated_user_repo.get_user_data("Charles")

def test_get_user_data_by_id(isolated_user_repo):
    """Tests if we can retrieve the correct user from the persistence layer. Also tests saving data to persistence layer in the process"""

    expected_data = {
        "c01" : {
            "username": "Charles",
            "wrong_data_form": "lol"
        },

        "d02" : {
            "id" : "d02",
            "username" : "harambe47",
            "name" : "Jane Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "superHardPassword1234",

            "account_is_active" : True
        }
    }
    isolated_user_repo.users = expected_data
    isolated_user_repo.save_to_file()
    retrieved_data = isolated_user_repo.get_user_data_from_id("d02")
    assert retrieved_data.model_dump(exclude_none=True) == expected_data["d02"]
    assert isinstance(retrieved_data, Developer)
    with pytest.raises(UserNotFoundError):
        retrieved_data = isolated_user_repo.get_user_data_from_id("james42")
    with pytest.raises(BadDataInPersistenceLayerError):
        retrieved_data = isolated_user_repo.get_user_data_from_id("c01")

def test_verify_user_account(isolated_user_repo):
    """Test that we can actually verify the role and activeness of users"""

    expected_data = {
        "c01" : {
            "username": "Charles",
            "wrong_data_form": "lol"
        },

        "d02" : {
            "id" : "d02",
            "username" : "harambe47",
            "name" : "Jane Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "superHardPassword1234",

            "account_is_active" : True
        },

        "a03" : {
            "id" : "a03",
            "username" : "harambe48",
            "name" : "Jane Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "superHardPassword1234",

            "account_is_active" : False,

            "managed_restaurants" : ["r01", "r02"]
        }
    }
    isolated_user_repo.users = expected_data
    isolated_user_repo.save_to_file()
    active = isolated_user_repo.generate_web_token("d02")
    deactivated = isolated_user_repo.generate_web_token("a03")
    non_existent= isolated_user_repo.generate_web_token("c03")
    broken = isolated_user_repo.generate_web_token("c01")
    assert isolated_user_repo.verify_user_account(active) == AccountStatusAndRole.ACTIVE_DEVELOPER
    assert isolated_user_repo.verify_user_account(deactivated) == AccountStatusAndRole.DEACTIVATED_RESTAURANT_ADMIN
    with pytest.raises(TokenBelongsToUnknownUserError):
        isolated_user_repo.verify_user_account(non_existent)
    with pytest.raises(BadDataInPersistenceLayerError):
        isolated_user_repo.verify_user_account(broken)

#################################################################################################################################################
## Test User Authentication related functions in Service Layer
#################################################################################################################################################

def test_user_login(isolated_user_service):
    """Test the login service"""

    expected_data = {
        "c01" : {
            "username": "Charles",
            "wrong_data_form": "lol"
        },

        "d02" : {
            "id" : "d02",
            "username" : "harambe47",
            "name" : "Jane Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "superHardPassword1234",

            "address" : "213-2532 Shoreline Dr",
            "city" : "Lake Country",
            "province" : "BC",
            "postal_code" : "V1V1V6",

            "account_is_active" : True,
            "reason_for_deactivation" : "",
            "balance" : 501.25
        },

        "a03" : {
            "id" : "a03",
            "username" : "harambe48",
            "name" : "Jane Doe",
            "email" : "janedoe47@gmail.com",
            "password" : "superHardPassword1234",

            "address" : "213-2532 Shoreline Dr",
            "city" : "Lake Country",
            "province" : "BC",
            "postal_code" : "V1V1V6",

            "account_is_active" : False,
            "reason_for_deactivation" : "",
            "balance" : 501.25,

            "managed_restaurants" : ["r01", "r02"]
        }
    }
    isolated_user_service.repository.users = expected_data
    non_existent_user = UserLogin(username="nick", password="password")
    wrong_password = UserLogin(username="harambe48", password="password")
    deactivated_account = UserLogin(username="harambe48", password="superHardPassword1234")
    active_account = UserLogin(username="harambe47", password="superHardPassword1234")
    with pytest.raises(UserAuthenticationError):
        isolated_user_service.user_login(non_existent_user) 
    with pytest.raises(UserAuthenticationError):
            isolated_user_service.user_login(wrong_password) 
    with pytest.raises(AccountNotActiveError):
        isolated_user_service.user_login(deactivated_account) 
    retrived_token = isolated_user_service.user_login(active_account)
    assert isolated_user_service.repository.get_id_from_token(retrived_token) == "d02"