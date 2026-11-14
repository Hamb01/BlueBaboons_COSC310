"""Repository layer for reading and writing to the user.Json file in the persistence layer"""

from datetime import datetime, timedelta, timezone
import json
import os
import secrets
import tempfile
from pathlib import Path
from typing import Optional

import jwt
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.exceptions import (
    BadDataInPersistenceLayerError,
    DataPersistenceError,
    ExpiredTokenError,
    TokenBelongsToUnknownUserError,
    TokenIsInvalidError,
    UserNotFoundError,
)
from app.schemas.user_schema import (
    AccountStatusAndRole,
    Customer,
    Developer,
    RestaurantAdmin,
    RestaurantOwner,
    SupportStaff,
    User,
)


class UserRepository:
    """Repository layer responsible for reading and writing user data"""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.master_file = self.data_dir / "Users.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.jwt_encode_key = secrets.token_urlsafe(64)

        if self.master_file.exists():
            try:
                self.users = self.check_user_json_persistence(str(self.master_file))
            except json.JSONDecodeError:
                self.users = {}
        else:
            self.users = {}
            self.save_to_file()

    def check_user_json_persistence(self, path: str) -> dict:
        """Check that the JSON persistence file can be opened and contains data."""
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not data:
            raise DataPersistenceError(str(self.master_file), "read")
        return data

    def save_to_file(self):
        """Persist all user data to the master JSON file."""
        fd, temp_path = tempfile.mkstemp(dir=self.data_dir, suffix=".temp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                json.dump(self.users, file, indent=4)
                file.flush()
                os.fsync(file.fileno())
                os.replace(temp_path, self.master_file)
        except (OSError, TypeError, ValueError) as exc:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass
            raise DataPersistenceError(str(self.master_file), "write") from exc

    def get_user_data(self, username: str) -> User:
        """
        get_user_data()
        -------------------

        Description:
            Retrieves the information of a specific user 

        Args: 
            username : string -> Unique username associated with the user's account

        Returns:
            User: A Pydantic model containing the user's account data.

        Raises: 
            UserNotFoundError -> No such user exists in our system
            BadDataInPersistenceLayerError -> the data stored in the persistence layer is incorrect
        """

        try:
            for user_id, data in self.users.items():
                if username == data["username"]:
                    first_character = user_id[0]
                    match first_character:
                        case 'c':
                            userdata = Customer.model_validate(data)
                        case 'a':
                            userdata = RestaurantAdmin.model_validate(data)
                        case 'o':
                            userdata = RestaurantOwner.model_validate(data)
                        case 'd':
                            userdata = Developer.model_validate(data)
                        case 's':
                            userdata = SupportStaff.model_validate(data)
                        case _:
                            raise UserNotFoundError(username)
                    return userdata

            raise UserNotFoundError(username)
        except ValidationError as exc:
            raise BadDataInPersistenceLayerError(
                str(self.master_file), "Data is in the wrong form"
            ) from exc

    def get_user_data_from_id(self, user_id: str) -> User:
        """
        get_user_data_from_id()
        -----------------------

        Description:
            Retrieves the information of a specific user from their ID

        Args: 
            id : string -> Unique id associated with the user's account

        Returns:
            User: A Pydantic model containing the user's account data.

        Raises: 
            UserNotFoundError -> No such user exists in our system
        """

        try:
            if user_id in self.users:
                data = self.users[user_id]
                first_character = user_id[0]
                match first_character:
                    case 'c':
                        userdata = Customer.model_validate(data)
                    case 'a':
                        userdata = RestaurantAdmin.model_validate(data)
                    case 'o':
                        userdata = RestaurantOwner.model_validate(data)
                    case 'd':
                        userdata = Developer.model_validate(data)
                    case 's':
                        userdata = SupportStaff.model_validate(data)
                    case _:
                        raise UserNotFoundError(user_id)
                return userdata
            raise UserNotFoundError(user_id)
        except ValidationError as exc:
            raise BadDataInPersistenceLayerError(
                str(self.master_file), "Data is in the wrong form"
            ) from exc

    def generate_web_token(self, user_id: str) -> str:
        """
        generate_web_token()
        -------------------

        Description:
            Creates a new json web token for a specific user
            This token can be used to authenticate a user and verify that they are authorized to do certain actions
            The tokens will expire after 15 minutes

        Args: 
            id : string -> Unique id associated with the user's account

        Returns:
            jwt -> a unique json web token for the user

        Raises: 
            none
        """
        payload = {
            "exp" : datetime.now(tz=timezone.utc) + timedelta(minutes = 15),
            "id": user_id
        }

        return jwt.encode(payload, self.jwt_encode_key, algorithm="HS512")

    def get_id_from_token(self, token: str) -> str:
        """
        get_id_from_token
        ---------------------

        Description: 
            Decodes JWT and gets the id of the user

        Args:
            token : JWT -> Json Web Token that the user is currently using

        Returns:
            string -> the ID of the user

        Raises: 
            none
        """

        try:
            decoded_token = jwt.decode(token, self.jwt_encode_key, algorithms=["HS512"])["id"]
        except jwt.ExpiredSignatureError as exc:
            raise ExpiredTokenError() from exc
        except jwt.InvalidTokenError as exc:
            raise TokenIsInvalidError() from exc

        return decoded_token
    def get_current_user(self, token: str) -> User:
        """
        get_current_user
        ---------------------

        Description: 
            Gets the userdata that is related to the id in the jwt

        Args:
            token : JWT -> Json Web Token that the user is currently using

        Returns:
            User -> a pydantic model of the user

        Raises: 
            TokenBelongsToUnknownUserError -> no user matched the Id provided by the token
            ExpiredTokenError -> Token is expired
        """

        id = self.get_id_from_token(token)
        return self.get_user_data_from_id(id)


    def verify_user_account(self, token) -> AccountStatusAndRole:
        """
        verify_user_account()
        ----------------------

        Description:
            verifies that the token belongs to a specific 

        Args: 
            token : JWT -> Json Web Token that the user is currently using

        Returns:
            AccountStatus -> current status of the account (ACTIVE or DEACTIVATED)

        Raises: 
            TokenBelongsToUnknownUserError -> the username specified belongs to a user that does not exist
            BadDataInPersistenceLayerError -> get_user_data_from_id returned the wrong type
        """

        try:
            decoded_token = jwt.decode(token, self.jwt_encode_key, algorithms=["HS512"])
            user_data = self.get_user_data_from_id(decoded_token["id"])
        except UserNotFoundError as exc:
            raise TokenBelongsToUnknownUserError() from exc
        except jwt.ExpiredSignatureError as exc:
            raise ExpiredTokenError() from exc
        except jwt.InvalidTokenError as exc:
            raise TokenIsInvalidError() from exc
        

        role_statuses = {
            Customer: (
                AccountStatusAndRole.ACTIVE_CUSTOMER,
                AccountStatusAndRole.DEACTIVATED_CUSTOMER,
            ),
            RestaurantOwner: (
                AccountStatusAndRole.ACTIVE_RESTAURANT_OWNER,
                AccountStatusAndRole.DEACTIVATED_RESTAURANT_OWNER,
            ),
            RestaurantAdmin: (
                AccountStatusAndRole.ACTIVE_RESTARUTANT_ADMIN,
                AccountStatusAndRole.DEACTIVATED_RESTAURANT_ADMIN,
            ),
            Developer: (
                AccountStatusAndRole.ACTIVE_DEVELOPER,
                AccountStatusAndRole.DEACTIVATED_DEVELLOPER,
            ),
            SupportStaff: (
                AccountStatusAndRole.ACTIVE_SUPPORT_STAFF,
                AccountStatusAndRole.DEACTIVATED_SUPPORT_STAFF,
            ),
        }
        for user_type, statuses in role_statuses.items():
            if isinstance(user_data, user_type):
                active_status, deactivated_status = statuses
                return (
                    active_status
                    if user_data.account_is_active
                    else deactivated_status
                )

        raise BadDataInPersistenceLayerError(
            str(self.master_file),
            "get_user_data_from_id returned the wrong type",
        )
