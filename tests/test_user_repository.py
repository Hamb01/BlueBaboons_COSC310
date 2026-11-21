"""Tests for user repository."""

import pytest
import base64
import hashlib
import json
import copy
from app.core.exceptions import (
    BadDataInPersistenceLayerError,
    DataPersistenceError,
    ExpiredTokenError,
    InvalidRequestError,
    TokenIsInvalidError,
    UserNameAlreadyTakenError,
    UserNotFoundError,
)
from app.schemas.user_schema import (
    AccountStatusAndRole,
    Customer,
    CustomerCreate,
    Developer,
    DeveloperCreate,
    RestaurantAdmin,
    RestaurantAdminCreate,
    RestaurantOwner,
    RestaurantOwnerCreate,
    SupportStaff,
    SupportStaffCreate,
    User,
    UserCreate,
    UserLogin,
)

expected_data = {
    "c01" : {
        "username": "Charles",
        "wrong_data_form": "lol"
    },

    "c02" : {
        "id" : "c02",
        "username" : "harambe47",
        "name" : "CustomerTwo",
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
        "name" : "CustomerThree",
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
        "username" : "superDuck48",
        "name" : "AdminOne",
        "email" : "janedoe47@gmail.com",
        "password" : "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
        "hash_salt" : "7OAKfGhKVTqWecOn5H7t4Q==",
        "account_is_active" : True,

        "managed_restaurants" : ["r01"]
    },

    "a02" : {
        "id" : "a02",
        "username" : "superDuck49",
        "name" : "AdminTwo",
        "email" : "janedoe47@gmail.com",
        "password" : "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
        "hash_salt" : "7OAKfGhKVTqWecOn5H7t4Q==",
        "account_is_active" : False,

        "managed_restaurants" : ["r01"]
    },

    "o01" : {
        "id" : "o01",
        "username" : "superDuck47",
        "name" : "OwnerOne",
        "email" : "janedoe47@gmail.com",
        "password" : "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
        "hash_salt" : "7OAKfGhKVTqWecOn5H7t4Q==",
        "account_is_active" : True,

        "managed_restaurants" : ["r01, r02"],
        "owned_restaurants" : ["r01"]
    },

    "o02" : {
        "id" : "o02",
        "username" : "superDuck47",
        "name" : "OwnerTwo",
        "email" : "janedoe47@gmail.com",
        "password" : "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
        "hash_salt" : "7OAKfGhKVTqWecOn5H7t4Q==",
        "account_is_active" : True,

        "managed_restaurants" : ["r01, r02"],
        "owned_restaurants" : ["r02"]
    },

    "d01" : {
        "id" : "d01",
        "username" : "superDuck47",
        "name" : "TheDeveloper",
        "email" : "janedoe47@gmail.com",
        "password" : "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
        "hash_salt" : "7OAKfGhKVTqWecOn5H7t4Q==",
        "account_is_active" : True,
    },
}

new_customer = CustomerCreate(
        username="SuperDans_SuperFan",
        name="new_customer",
        email="legally_distinct_email@gmail.com",
        password="pigeonLover1973",
        address="147 Oak st",
        city="penticton",
        province="British Columbia",
        postal_code="H0H0H0"
    )

incomplete_customer = UserCreate(
    username="legally_distinct_customer",
    name="incomplete_customer",
    email="legally_distinct_email@gmail.com",
    password="not-a-supported-user-type"
)

duplicate_customer = CustomerCreate(
    username="SuperDans_SuperFan",
    name="new_customer",
    email="legally_distinct_email@gmail.com",
    password="pigeonLover1973",
    address="147 Oak st",
    city="penticton",
    province="British Columbia",
    postal_code="H0H0H0"
)

new_admin = RestaurantAdminCreate(
    username="super_cat",
    name="new_customer",
    email="legally_distinct_email@gmail.com",
    password="pigeonLover1973",
    managed_restaurants=["r01"]
)

new_owner = RestaurantOwnerCreate(
    username="SuperDog",
    name="new_customer",
    email="legally_distinct_email@gmail.com",
    password="pigeonLover1973",
    managed_restaurants=[""],
    owned_restaurants=[""]
)

new_developer = DeveloperCreate(
    username="OneOfTheDevsEver",
    name="new_customer",
    email="legally_distinct_email@gmail.com",
    password="pigeonLover1973",
)

new_support_staff = SupportStaffCreate(
    username="DeliveryGuy",
    name="new_customer",
    email="legally_distinct_email@gmail.com",
    password="pigeonLover1973",
)

new_ids = ["c04", "a03", "o03", "d02", "s01"]


def test_add_new_user(isolated_user_repo):
    """Test that the created user has all of it's data in the correct form"""

    isolated_user_repo.store.save(expected_data)

    customer = isolated_user_repo.add_new_user(new_customer)
    admin = isolated_user_repo.add_new_user(new_admin)
    owner = isolated_user_repo.add_new_user(new_owner)
    developer = isolated_user_repo.add_new_user(new_developer)
    support_staff = isolated_user_repo.add_new_user(new_support_staff)

    with pytest.raises(InvalidRequestError):
        isolated_user_repo.add_new_user(incomplete_customer)
    with pytest.raises(UserNameAlreadyTakenError):
        isolated_user_repo.add_new_user(duplicate_customer)

    for id in new_ids:
        assert id in isolated_user_repo.users.keys()

    assert customer.account_is_active
    assert not admin.account_is_active
    assert owner.model_dump() == isolated_user_repo.users["o03"]
    assert isinstance(developer, Developer)
    assert not support_staff.password == new_support_staff.password #verify password is scrambled

    stored_password = base64.b64decode(owner.password.encode('utf-8'))
    
    # hash entered password and see if they are the same
    entered_password = hashlib.pbkdf2_hmac(
        "sha256",
        new_owner.password.encode("utf-8"),
        base64.b64decode(owner.hash_salt.encode("utf-8")),
        600_000
    )

    assert stored_password == entered_password
