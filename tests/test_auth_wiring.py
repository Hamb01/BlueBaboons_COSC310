"""Regression tests for the login dependency wiring.

The shared `client` fixture overrides both get_user_repository and get_user_service, so it
never runs the real wiring. Two bugs hid behind that: get_user_repository returned the
UserRepository class instead of an instance, and the login route took `service=get_user_service`
instead of `Depends(get_user_service)`. Either one made every real login return 500.
"""
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.deps import get_current_user, get_user_repository
from app.main import app
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import User

ACTIVE_CUSTOMER = {
    "d02": {
        "id": "d02",
        "username": "harambe47",
        "name": "Jane Doe",
        "email": "janedoe47@gmail.com",
        "password": "u5e2htydiOSUbjOGkdOJsfAL0kniyUC3BnuNWnekB7s=",
        "hash_salt": "7OAKfGhKVTqWecOn5H7t4Q==",
        "address": "213-2532 Shoreline Dr",
        "city": "Lake Country",
        "province": "BC",
        "postal_code": "V1V1V6",
        "account_is_active": True,
        "reason_for_deactivation": "",
        "balance": 501.25,
    }
}


def test_get_user_repository_returns_an_instance():
    assert isinstance(get_user_repository(), UserRepository)


def test_get_current_user_returns_the_authenticated_user():
    user = User(
        id="u01",
        username="user",
        name="Test User",
        email="user@example.com",
        password="hashed",
        hash_salt="salt",
        account_is_active=True,
    )
    repository = Mock(spec=UserRepository)
    repository.get_current_user.return_value = user

    assert get_current_user(token="valid-token", repository=repository) is user


def test_get_current_user_without_token_does_not_default_to_admin():
    repository = Mock(spec=UserRepository)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=None, repository=repository)

    assert exc_info.value.status_code == 401
    repository.get_current_user.assert_not_called()


def test_login_route_uses_the_real_user_service(isolated_user_repo):
    """Only the repository is replaced, so get_user_service and Depends() run for real."""
    isolated_user_repo.users = ACTIVE_CUSTOMER
    app.dependency_overrides[get_user_repository] = lambda: isolated_user_repo
    try:
        with TestClient(app) as client:
            wrong = client.post("/auth/login", json={"username": "harambe47", "password": "nope"})
            right = client.post("/auth/login",
                                json={"username": "harambe47", "password": "superHardPassword1234"})
    finally:
        app.dependency_overrides.clear()

    assert wrong.status_code == 401
    assert right.status_code == 200
    assert right.json()
