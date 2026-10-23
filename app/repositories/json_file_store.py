import json
import os
from pathlib import Path
from typing import Any, Dict

from app.core.exceptions import DataPersistenceError


class JsonFileStore:
    """Shared load/save helper for repositories that keep a dict of records in one JSON file.

    Records are stored as {"<id>": {...record...}}, the same shape as Restaurants.json.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        """Return every record. A missing file means "no records yet"."""
        if not self.path.exists():
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            # Fail loudly: silently returning {} here would let the next save wipe the file.
            raise DataPersistenceError(f"Could not read {self.path.name}: {error}") from error

    def save(self, records: Dict[str, Any]) -> None:
        """Write every record atomically.

        Data is written to a temporary file first and then swapped in, so a crash
        mid-write can never leave a half-written (corrupted) JSON file behind.
        """
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(records, file, indent=4, default=str)
            os.replace(temp_path, self.path)
        except OSError as error:
            raise DataPersistenceError(f"Could not write {self.path.name}: {error}") from error

    @staticmethod
    def next_id(records: Dict[str, Any], prefix: str) -> str:
        """Next stable ID such as 'u03', following the existing 'r01' / 'm01' convention.

        IDs are never reused, because the number is one past the highest existing one.
        """
        numbers = [
            int(key[len(prefix):]) for key in records
            if key.startswith(prefix) and key[len(prefix):].isdigit()
        ]
        next_number = max(numbers) + 1 if numbers else 1
        return f"{prefix}{next_number:02d}"
