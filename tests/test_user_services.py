"""Tests for user services."""

import pytest
import json
import copy
from app.core.exceptions import (
    AccountNotActiveError,
    BadDataInPersistenceLayerError,
    TokenBelongsToUnknownUserError,
    UserAuthenticationError,
    UserNotAuthorizedError,
    UserNotFoundError,
)
from app.schemas.user_schema import AccountStatusAndRole, CustomerUpdate, Developer, UserLogin, CustomerResponse
from pydantic import ValidationError
ADDRESS_FIELDS = ["address", "city", "province", "postal_code"]
EDITABLE_FIELDS = ["name", "email", *ADDRESS_FIELDS]
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
@pytest.fixture
def seeded_service(isolated_user_service):
    """isolated_user_service pre-loaded with the valid customers from expected_data."""
    isolated_user_service.repository.users = {
        user_id: copy.deepcopy(expected_data[user_id]) for user_id in ("c02", "c03")
    }
    isolated_user_service.repository.save_to_file()
    return isolated_user_service

def test_get_customer(isolated_user_service):
    """Test the ability to retrive customer data for a specific customer"""


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


@pytest.mark.parametrize("field", ADDRESS_FIELDS)
@pytest.mark.parametrize("value", ["", "   ", "\t\n", None])
def test_update_rejects_empty_address_parts(field, value):
    """Empty, whitespace-only and explicit null address parts are rejected."""
    with pytest.raises(ValidationError):
        CustomerUpdate(**{field: value})


def test_update_trims_whitespace():
    assert CustomerUpdate(address="  1 New Rd  ").address == "1 New Rd"


def test_update_only_contains_fields_that_were_sent():
    """Fields left out of the request are not set, so they won't overwrite anything."""
    assert CustomerUpdate(city="Kelowna").model_dump(exclude_unset=True) == {"city": "Kelowna"}


def test_update_customer_returns_updated_customer(seeded_service):
    current_user = seeded_service.repository.get_user_data_from_id("c02")

    response = seeded_service.update_customer(
        "c02", CustomerUpdate(address="1 New Rd", city="Kelowna"), current_user
    )

    assert isinstance(response, CustomerResponse)
    assert response.address == "1 New Rd"
    assert response.city == "Kelowna"
    assert response.name == "Jane Doe"            # untouched
    assert response.postal_code == "V1V1V6"       # untouched


def test_update_customer_is_written_to_file(seeded_service):
    current_user = seeded_service.repository.get_user_data_from_id("c02")

    seeded_service.update_customer("c02", CustomerUpdate(address="1 New Rd"), current_user)

    # Read the JSON file directly (repository.master_file is the path to
    # Users.json) to prove the change was really saved, not just held in memory.
    on_disk = json.loads(seeded_service.repository.master_file.read_text(encoding="utf-8"))["c02"]
    assert on_disk["address"] == "1 New Rd"
    # Partial update: every other stored field is exactly as before.
    for key, original in expected_data["c02"].items():
        if key != "address":
            assert on_disk[key] == original, f"{key} was changed"


def test_update_customer_survives_restart(seeded_service):
    current_user = seeded_service.repository.get_user_data_from_id("c02")
    seeded_service.update_customer("c02", CustomerUpdate(address="1 New Rd"), current_user)

    restarted_repo = restart(seeded_service)

    assert restarted_repo.get_user_data_from_id("c02").address == "1 New Rd"


def test_update_customer_with_empty_body_changes_nothing(seeded_service):
    current_user = seeded_service.repository.get_user_data_from_id("c02")

    seeded_service.update_customer("c02", CustomerUpdate(), current_user)

    # Read Users.json directly: an empty body must leave the record untouched.
    on_disk = json.loads(seeded_service.repository.master_file.read_text(encoding="utf-8"))["c02"]
    assert on_disk == expected_data["c02"]

def restart(service):
    """Simulate a server restart: build a brand-new repository pointed at the
    same data folder, so it has to load everything back from Users.json.
    UserRepository's constructor only takes data_dir."""
    repo_class = type(service.repository)
    return repo_class(service.repository.data_dir)
