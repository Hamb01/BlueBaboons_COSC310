"""Repository layer for reading and writing to the user.Json file in the persistence layer"""

import json
import os
import tempfile
import secrets
import jwt
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import ValidationError
from datetime import datetime, timezone, timedelta

from app.core.config import get_settings
from app.core.exceptions import DataPersistenceError, BadDataInPersistenceLayerError, UserNotFoundError, TokenBelongsToUnknownUserError
from app.schemas.user_schema import User, Customer, RestaurantOwner, RestaurantAdmin, Developer, SupportStaff, AccountStatusAndRole

class UserRepository :
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

    def get_user_data(self, username : str) -> User:
        """
        get_user_data()
        -------------------

        Description:
            Retrieves the information of a specific user 

        Args: 
            username : string -> Unique username associated with the user's account

        Returns:
            User -> All data related to the user, returned as a pydantic model (either a customer, restaurant_admin, developer or support_staff)

        Raises: 
            UserNotFoundError -> No such user exists in our system
            BadDataInPersistenceLayerError -> the data stored in the persistence layer is incorrect
        """

        try:
            for id, data in self.users.items():
                if username == self.users[id]["username"]:
                    first_character = id[0]
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
                            raise UserNotFoundError
                    return userdata
                
            raise UserNotFoundError(username)
        except ValidationError:
            raise BadDataInPersistenceLayerError(str(self.master_file), "Data is in the wrong form")

    def get_user_data_from_id(self, id : str) -> User:
        """
        get_user_data_from_id()
        -----------------------

        Description:
            Retrieves the information of a specific user from their ID

        Args: 
            id : string -> Unique id associated with the user's account

        Returns:
            User -> All data related to the user, returned as a pydantic model (either a customer, restaurant_admin, developer or support_staff)

        Raises: 
            UserNotFoundError -> No such user exists in our system
        """

        try:
            if id in self.users:
                data = self.users[id]
                first_character = id[0]
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
                        raise UserNotFoundError(id)
                return userdata
            raise UserNotFoundError(id)
        except ValidationError:
            raise BadDataInPersistenceLayerError(str(self.master_file), "Data is in the wrong form")


    def generate_web_token(self, id : str):
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
            "id" : id
        }

        return jwt.encode(payload, self.jwt_encode_key, algorithm="HS512")

    def get_id_from_token(self, token) -> str:
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
        return jwt.decode(token, self.jwt_encode_key, algorithms=["HS512"])["id"]
        

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

        decoded_token = jwt.decode(token, self.jwt_encode_key, algorithms=["HS512"])

        try:
            user_data = self.get_user_data_from_id(decoded_token["id"])
        except UserNotFoundError as exc:
            raise TokenBelongsToUnknownUserError() from exc

        if isinstance(user_data, Customer):
            if user_data.account_is_active:
                return AccountStatusAndRole.ACTIVE_CUSTOMER
            else:
                return AccountStatusAndRole.DEACTIVATED_CUSTOMER
        elif isinstance(user_data, RestaurantOwner):
            if user_data.account_is_active:
                return AccountStatusAndRole.ACTIVE_RESTAURANT_OWNER
            else:
                return AccountStatusAndRole.DEACTIVATED_RESTAURANT_OWNER
        elif isinstance(user_data, RestaurantAdmin):
            if user_data.account_is_active:
                return AccountStatusAndRole.ACTIVE_RESTAURANT_ADMIN
            else:
                return AccountStatusAndRole.DEACTIVATED_RESTAURANT_ADMIN
        elif isinstance(user_data, Developer):
            if user_data.account_is_active:
                return AccountStatusAndRole.ACTIVE_DEVELOPER
            else:
                return AccountStatusAndRole.DEACTIVATED_DEVELLOPER
        elif isinstance(user_data, SupportStaff):
                if user_data.account_is_active:
                    return AccountStatusAndRole.ACTIVE_SUPPORT_STAFF
                else:
                    return AccountStatusAndRole.DEACTIVATED_SUPPORT_STAFF
        else:
            raise BadDataInPersistenceLayerError(str(self.master_file), "get_user_data_from_id returned the wrong type")
    

        
