"""Module to test User related endpoints"""

import pytest

from app.core.exceptions import (
    AccountNotActiveError,
    BadDataInPersistenceLayerError,
    TokenBelongsToUnknownUserError,
    UserAuthenticationError,
    UserNotAuthorizedError,
    UserNotFoundError,
)
from app.schemas.user_schema import (
    AccountStatusAndRole,
    Developer,
    UserLogin,
    CustomerResponse,
)

def test_deactivated_user_cant_add_to_cart(client):
    """Multisystem test to verify that deactivated users cannot add items to a cart"""
    pass



