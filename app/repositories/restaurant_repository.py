"""Repository layer responsible for reading restaurant data from storage."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.core.exceptions import DataPersistenceError, RestaurantNotFoundError


class RestaurantRepository:
    """Repository layer responsible for reading and writing restaurant data."""

    # Coding Notes:
    # Local file path is defined as a constant that points toward the master JSON.
    # Restaurant records are maintained in JSON and loaded into memory at startup.
    # The repository layer acts as the storage abstraction for restaurant data.

    def check_restaurant_json_persistence(self, path: str) -> dict:
        """Check that the JSON persistence file can be opened and contains data."""
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not data:
            raise DataPersistenceError(str(self.master_file), "read")
        return data

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.master_file = self.data_dir / "Restaurants.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if self.master_file.exists():
            try:
                self.restaurants = self.check_restaurant_json_persistence(str(self.master_file))
            except json.JSONDecodeError:
                self.restaurants = {}
        else:
            self.restaurants = {}
            self.save_to_file()

    def get_restaurant_data(self, restaurant_id: str) -> Dict[str, Any]:
        """Return restaurant data for the given restaurant id."""
        if restaurant_id in self.restaurants:
            return self.restaurants[restaurant_id]
        raise RestaurantNotFoundError(restaurant_id)

    def save_to_file(self):
        """Persist all restaurant data to the master JSON file."""
        fd, temp_path = tempfile.mkstemp(dir=self.data_dir, suffix=".temp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                json.dump(self.restaurants, file, indent=4)
                file.flush()
                os.fsync(file.fileno())
                os.replace(temp_path, self.master_file)
        except (OSError, TypeError, ValueError) as exc:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass
            raise DataPersistenceError(str(self.master_file), "write") from exc

    def get_all_restaurant(self) -> List[Dict[str, Any]]:
        """Return all restaurants currently stored."""
        return list(self.restaurants.values())

    def generate_restaurant_id(self) -> str:
        """Return the next unique restaurant id."""
        existing_ids = [
            int(rest_id[1:])
            for rest_id in self.restaurants.keys()
            if rest_id.startswith("r") and rest_id[1:].isdigit()
        ]
        next_num = max(existing_ids) + 1 if existing_ids else 1
        return f"r{next_num:02d}"

    def create_restaurant(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a restaurant record and persist it to disk."""
        restaurant_id = self.generate_restaurant_id()
        restaurant_data["id"] = restaurant_id
        self.restaurants[restaurant_id] = restaurant_data
        self.save_to_file()
        return restaurant_data

    def update_restaurant(
        self,
        restaurant_id: str,
        update_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update an existing restaurant while preserving its id."""
        current_data = self.get_restaurant_data(restaurant_id)

        for key, value in update_data.items():
            if key == "id":
                continue
            current_data[key] = value

        current_data["id"] = restaurant_id
        self.restaurants[restaurant_id] = current_data
        self.save_to_file()
        return current_data
