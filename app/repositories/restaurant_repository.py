"""Repository layer responsible for reading restaurant data from storage."""
from json import JSONDecodeError
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.repositories.jsonstore import JsonStore

from app.core.config import get_settings
from app.core.exceptions import DataPersistenceError, RestaurantNotFoundError


class RestaurantRepository:
    """Repository layer responsible for reading and writing restaurant data."""

    # Coding Notes:
    # Local file path is defined as a constant that points toward the master JSON.
    # Restaurant records are maintained in JSON and loaded into memory at startup.
    # The repository layer acts as the storage abstraction for restaurant data.

    def check_restaurant_json_persistence(self, path: str) -> dict:
        """
        check_restaurant_json_persistence
        -----------------------------------

        Description:
            Verifies that our JSON persistence file can be opened and contains data

        Args: 
            path : string -> path to the persistence file

        Returns:
            data : dict -> Data stored in the JSON file

        Raises: 
            DataPersistenceError -> The JSON file contained no data
        """
        with open(path, "r", encoding="utf-8") as file:
            data = JsonStore(path).load()
        if not data:
            raise DataPersistenceError("Persistence failed: Dict is empty")
        return data

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.master_file = self.data_dir / "Restaurants.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.store = JsonStore(self.master_file)          # ← line 47, fixed
        self.restaurants = self.store.load()

        if self.master_file.exists():
            try:
                self.restaurants = self.check_restaurant_json_persistence(str(self.master_file))
            except DataPersistenceError:
                self.restaurants = {}
        else:
            self.restaurants = {}
            self.save_to_file()

    def get_restaurant_data(self, restaurant_id: str) -> Dict[str, Any]:
        """
        get_restaurant_data
        -------------------

        Description:
            reads the data for a restaurant from the persistence layer

        Args: 
            restaurant_id : string -> Unique ID belonging to the specific restaurant

        Returns:
            data : Dict[str, Any] -> Data related to the restaurant

        Raises: 
            RestaurantNotFoundError -> Restaurant is not stored in the restaurants.json file
        """
        if restaurant_id in self.restaurants:
            return self.restaurants[restaurant_id]
        raise RestaurantNotFoundError(restaurant_id)

    def save_to_file(self):
        """
        save_to_file
        -------------------

        Description:
            saves our restaurant repository object to the restaurants.JSON file

        Args:
            void

        Returns:
            void

        Raises:
            DataPersistenceError -> Error while saving to the file
        """
        self.store.save(self.restaurants)

    def get_all_restaurant(self) -> List[Dict[str, Any]]:
        """
        get_all_restaurant
        -------------------

        Description:
            Retrieves the data for all of the restaurants stored in the system

        Args: 
            void

        Returns:
            List[Dict[str, Any]] -> all of the data for all restaurants in the system

        Raises: 
            none
        """
        return list(self.restaurants.values())

    def generate_restaurant_id(self) -> str:
        """
        generate_restaurant_id
        -----------------------

        Description:
            Generates a unique ID for a new restaunt

        Args: 
            void

        Returns:
            string -> the ID for the new restaurant

        Raises: 
            none
        """
        existing_ids = [
            int(rest_id[1:])
            for rest_id in self.restaurants.keys()
            if rest_id.startswith("r") and rest_id[1:].isdigit()
        ]
        next_num = max(existing_ids) + 1 if existing_ids else 1
        return f"r{next_num:02d}"

    def create_restaurant(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        create_restaurant
        -------------------

        Description:
            creates a new restaurant and saves it to the persistance layer

        Args:
            restaurant_data : Dict[str, Any] -> Details about the new restaurant (defined in restaurant_shemas)

        Returns:
            Dict[str, Any] -> The data for the restaurant you just created

        Raises:
            DataPersistenceError -> There was an error when writing to the JSON file
        """
        restaurant_id = self.generate_restaurant_id()
        new_restaurant = {**restaurant_data, "id": restaurant_id}
        updated = {**self.restaurants, restaurant_id: new_restaurant}
        self.store.save(updated)
        self.restaurants = updated
        return new_restaurant

    def update_restaurant(
        self,
        restaurant_id: str,
        update_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        update_restaurant
        -------------------

        Description:
            updates some of the information pertaining to a specific restaurant

        Args:
            restaurant_id : string -> Unique ID belonging to the specific restaurant
            update_data : Dict[str, Any] -> the data field(s) to be updated

        Returns:
            Dict[str, Any] -> The data for the restaurant you just created

        Raises:
            RestaurantNotFoundError -> The restaurant is not stored in our persistence layer
            DataPersistenceError -> There was an error when writing to the JSON file
        """
        current_data = self.get_restaurant_data(restaurant_id)

        for key, value in update_data.items():
            if key == "id":
                continue
            current_data[key] = value

        current = self.get_restaurant_data(restaurant_id)
        changes = {k: v for k, v in update_data.items() if k != "id"}
        new_restaurant = {**current, **changes, "id": restaurant_id}
        updated = {**self.restaurants, restaurant_id: new_restaurant}
        self.store.save(updated)
        self.restaurants = updated
        return new_restaurant
