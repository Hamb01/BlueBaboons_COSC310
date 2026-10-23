from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.repositories.json_file_store import JsonFileStore


class UserRepository:
    """Repository layer for user accounts.

    Owner: Person A (customers + auth).
    Storage: data/Users.json
    TODO: what does one stored user record look like? (Write an example in this docstring once decided.)
    TODO: where do sign-in tokens/sessions live, if anywhere? Should that file be committed to git?
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.users = JsonFileStore(self.data_dir / "Users.json")

    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("UserRepository.get_by_id")

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        # TODO: is "Sam@Example.com" the same account as "sam@example.com"?
        raise NotImplementedError("UserRepository.get_by_email")

    def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("UserRepository.create")

    def update(self, user_id: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("UserRepository.update")

    # TODO: add whatever methods auth needs (e.g. for tokens) once you've designed sign-in.
