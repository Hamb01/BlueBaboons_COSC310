"""Tests for user services."""

import pytest
import json
import copy
from app.core.exceptions import (
    AccountNotActiveError,
    BadDataInPersistenceLayerError,
    TokenBelongsToUnknownUserError,
    UserNameAlreadyTakenError,
    UserAuthenticationError,
    UserNotAuthorizedError,
    UserNotFoundError,
)
from app.schemas.user_schema import (
    AccountStatusAndRole,
    Customer,
    CustomerCreate,
    CustomerUpdate,
    Developer,
    DeveloperCreate,
    RestaurantAdmin,
    RestaurantAdminCreate,
    RestaurantAdminResponse,
    RestaurantOwner,
    RestaurantOwnerCreate,
    RestaurantOwnerResponse,
    SupportStaff,
    SupportStaffCreate,
    UserLogin,
    UserResponse,
    CustomerResponse,
)
from pydantic import ValidationError
ADDRESS_FIELDS = ["address", "city", "province", "postal_code"]
EDITABLE_FIELDS = ["name", "email", *ADDRESS_FIELDS]
# A complete, valid address. CustomerUpdate requires all four address parts,
# so every update in these tests starts from this and overrides what it needs.
NEW_ADDRESS = {
    "address": "1 New Rd",
    "city": "Kelowna",
    "province": "BC",
    "postal_code": "V1Y1A1",
}
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
    isolated_user_service.repository.store.save(isolated_user_service.repository.users)
    return isolated_user_service

def test_get_customer(isolated_user_service):
    """Test the ability to retrive customer data for a specific customer"""


    isolated_user_service.repository.users = expected_data
    isolated_user_service.repository.store.save(isolated_user_service.repository.users)

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
    isolated_user_service.repository.store.save(isolated_user_service.repository.users)

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
    """Empty, whitespace-only and explicit null address parts are rejected,
    even when the other three address parts are valid."""
    with pytest.raises(ValidationError):
        CustomerUpdate(**{**NEW_ADDRESS, field: value})


@pytest.mark.parametrize("field", ADDRESS_FIELDS)
def test_update_requires_every_address_part(field):
    """Leaving out any one address part is rejected (a 422 at the endpoint)."""
    missing_one = {key: value for key, value in NEW_ADDRESS.items() if key != field}
    with pytest.raises(ValidationError):
        CustomerUpdate(**missing_one)


def test_update_rejects_empty_body():
    """An update must always include the address."""
    with pytest.raises(ValidationError):
        CustomerUpdate()


def test_update_rejects_name_or_email_without_address():
    """Changing name/email alone is not allowed; the address must come with it."""
    with pytest.raises(ValidationError):
        CustomerUpdate(name="New Name", email="new@example.com")


def test_update_trims_whitespace():
    update = CustomerUpdate(**{**NEW_ADDRESS, "address": "  1 New Rd  "})
    assert update.address == "1 New Rd"


def test_update_leaves_unsent_optional_fields_unset():
    """name and email are optional: if they aren't sent, they won't overwrite anything."""
    assert CustomerUpdate(**NEW_ADDRESS).model_dump(exclude_unset=True) == NEW_ADDRESS


def test_update_customer_returns_updated_customer(seeded_service):
    current_user = seeded_service.repository.get_user_data_from_id("c02")

    response = seeded_service.update_customer("c02", CustomerUpdate(**NEW_ADDRESS), current_user)

    assert isinstance(response, CustomerResponse)
    for field in ADDRESS_FIELDS:
        assert getattr(response, field) == NEW_ADDRESS[field]
    assert response.name == "Jane Doe"                  # untouched
    assert response.email == "janedoe47@gmail.com"      # untouched


def test_update_customer_is_written_to_file(seeded_service):
    current_user = seeded_service.repository.get_user_data_from_id("c02")

    seeded_service.update_customer("c02", CustomerUpdate(**NEW_ADDRESS), current_user)

    # Read the JSON file directly (repository.master_file is the path to
    # Users.json) to prove the change was really saved, not just held in memory.
    on_disk = json.loads(seeded_service.repository.master_file.read_text(encoding="utf-8"))["c02"]
    for field in ADDRESS_FIELDS:
        assert on_disk[field] == NEW_ADDRESS[field]
    # Every non-address field is exactly as before.
    for key, original in expected_data["c02"].items():
        if key not in ADDRESS_FIELDS:
            assert on_disk[key] == original, f"{key} was changed"


def test_update_customer_survives_restart(seeded_service):
    current_user = seeded_service.repository.get_user_data_from_id("c02")
    seeded_service.update_customer("c02", CustomerUpdate(**NEW_ADDRESS), current_user)

    restarted_repo = restart(seeded_service)

    assert restarted_repo.get_user_data_from_id("c02").address == NEW_ADDRESS["address"]


def test_update_email_with_unchanged_address(seeded_service):
    """The frontend resends the preloaded address; only the email should change."""
    current_user = seeded_service.repository.get_user_data_from_id("c02")
    current_address = {field: expected_data["c02"][field] for field in ADDRESS_FIELDS}

    seeded_service.update_customer(
        "c02", CustomerUpdate(**current_address, email="new@example.com"), current_user
    )

    on_disk = json.loads(seeded_service.repository.master_file.read_text(encoding="utf-8"))["c02"]
    assert on_disk == {**expected_data["c02"], "email": "new@example.com"}


def test_create_new_customer_returns_public_response_and_persists_account(
    isolated_user_service,
):
    new_customer = CustomerCreate(
        username="new_service_customer",
        name="New Customer",
        email="customer@example.com",
        password="customer-password",
        address="12 Main St",
        city="Kelowna",
        province="BC",
        postal_code="V1Y1A1",
    )

    response = isolated_user_service.create_new_customer(new_customer)

    assert response.model_dump() == {
        "username": "new_service_customer",
        "name": "New Customer",
        "email": "customer@example.com",
        "account_is_active": True,
        "address": "12 Main St",
        "city": "Kelowna",
        "province": "BC",
        "postal_code": "V1Y1A1",
        "balance": 99.99,
    }

    stored_customer = isolated_user_service.repository.get_user_data(
        new_customer.username
    )
    assert isinstance(stored_customer, Customer)
    assert new_customer.password == "customer-password"
    assert stored_customer.password != new_customer.password
    assert isolated_user_service.repository.check_login_info(
        UserLogin(username=new_customer.username, password=new_customer.password),
        stored_customer,
    )

    on_disk = json.loads(
        isolated_user_service.repository.master_file.read_text(encoding="utf-8")
    )
    assert on_disk[stored_customer.id] == stored_customer.model_dump()


def test_create_new_customer_propagates_duplicate_username_error(
    isolated_user_service,
):
    new_customer = CustomerCreate(
        username="duplicate_service_customer",
        name="New Customer",
        email="customer@example.com",
        password="customer-password",
        address="12 Main St",
        city="Kelowna",
        province="BC",
        postal_code="V1Y1A1",
    )

    isolated_user_service.create_new_customer(new_customer)

    with pytest.raises(UserNameAlreadyTakenError):
        isolated_user_service.create_new_customer(new_customer)


@pytest.mark.parametrize(
    ("new_user", "response_type", "stored_type", "expected_extra"),
    [
        (
            RestaurantAdminCreate(
                username="new_admin",
                name="New Admin",
                email="admin@example.com",
                password="test-password",
                managed_restaurants=["r01"],
            ),
            RestaurantAdminResponse,
            RestaurantAdmin,
            {"managed_restaurants": ["r01"]},
        ),
        (
            RestaurantOwnerCreate(
                username="new_owner",
                name="New Owner",
                email="owner@example.com",
                password="test-password",
                managed_restaurants=["r01"],
                owned_restaurants=["r01"],
            ),
            RestaurantOwnerResponse,
            RestaurantOwner,
            {"managed_restaurants": ["r01"], "owned_restaurants": ["r01"]},
        ),
        (
            DeveloperCreate(
                username="new_developer",
                name="New Developer",
                email="developer@example.com",
                password="test-password",
            ),
            UserResponse,
            Developer,
            {},
        ),
        (
            SupportStaffCreate(
                username="new_support_staff",
                name="New Support Staff",
                email="staff@example.com",
                password="test-password",
            ),
            UserResponse,
            SupportStaff,
            {},
        ),
    ],
)
def test_create_new_user_returns_role_specific_response(
    isolated_user_service, new_user, response_type, stored_type, expected_extra
):
    response = isolated_user_service.create_new_user(new_user)

    assert isinstance(response, response_type)
    assert response.model_dump() == {
        "username": new_user.username,
        "name": new_user.name,
        "email": new_user.email,
        **expected_extra,
    }

    stored_user = isolated_user_service.repository.get_user_data(new_user.username)
    assert isinstance(stored_user, stored_type)
    assert not stored_user.account_is_active
    assert stored_user.password != new_user.password
    assert isolated_user_service.repository.check_login_info(
        UserLogin(username=new_user.username, password=new_user.password),
        stored_user,
    )
    assert new_user.password == "test-password"

    on_disk = json.loads(
        isolated_user_service.repository.master_file.read_text(encoding="utf-8")
    )
    assert on_disk[stored_user.id] == stored_user.model_dump()


def restart(service):
    """Simulate a server restart: build a brand-new repository pointed at the
    same data folder, so it has to load everything back from Users.json.
    UserRepository's constructor only takes data_dir."""
    repo_class = type(service.repository)
    return repo_class(service.repository.data_dir)
