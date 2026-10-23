from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.repositories.json_file_store import JsonFileStore


class UserRepository:
    """Repository layer for user accounts (customers, restaurant owners, admins).

    Owner: Person A (customers + auth).
    Storage: data/Users.json  -> {"u01": {"id", "name", "email", "password_hash",
                                          "role", "restaurant_id", "delivery_address", "is_active"}}
             data/Sessions.json -> {"<token>": "<user_id>"}
    IDs use the prefix 'u' (u01, u02, ...) via JsonFileStore.next_id.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.users = JsonFileStore(self.data_dir / "Users.json")
        self.sessions = JsonFileStore(self.data_dir / "Sessions.json")

    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Return the stored user record, or None if it does not exist."""
        raise NotImplementedError("UserRepository.get_by_id")

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Return the user with this email (compare case-insensitively), or None."""
        raise NotImplementedError("UserRepository.get_by_email")

    def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a new stable ID, save the record, and return it (including the ID)."""
        raise NotImplementedError("UserRepository.create")

    def update(self, user_id: str, changes: Dict[str, Any]) -> Dict[str, Any]:
        """Apply changes (never the ID) to an existing user, save, and return the updated record."""
        raise NotImplementedError("UserRepository.update")

    def save_session(self, token: str, user_id: str) -> None:
        """Remember that this token belongs to this user."""
        raise NotImplementedError("UserRepository.save_session")

    def get_user_id_for_token(self, token: str) -> Optional[str]:
        """Return the user ID a token belongs to, or None for an unknown token."""
        raise NotImplementedError("UserRepository.get_user_id_for_token")
