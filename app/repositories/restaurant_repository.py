import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.exceptions import DomainError, RestaurantNotFoundError, DataPersistenceError
from app.core.config import get_settings

class RestaurantRepository:
    """Repository layer responsible for reading restaurant data from storage."""

    def __init__(self, data_dir: Optional[Path] = None):

        # Path to the data directory
        self.data_dir = data_dir or get_settings().data_dir
        
        with open(self.data_dir / "Restaurant_Names.json", "r", encoding="utf-8") as file:
           # Key:   Restaurant id 
           # Value: Restarant_Name.json
           self.restaurant_names = json.load(file)

        with open(self.data_dir / "Restaurant_Keys.json", "r", encoding="utf-8") as file:
            # Key:   Restaurant_Name
            # Value: Restaurant id
            self.restaurant_keys = json.load(file)


    def get_restaurant_data(self, id: str) -> Dict[str, Any]:
        """Method to return restaurant data. can be fed with either the restaurant name or id"""

        if id in self.restaurant_names:
          file_name = self.restaurant_names.get(id) + ".json"
        elif id in self.restaurant_keys:
          file_name = self.restaurant_names.get(self.restaurant_keys.get(id)) + ".json"
        else:
           raise RestaurantNotFoundError(f"Restaurant does not exist: {id}")
       
        path = self.data_dir / "restaurants" / file_name 
       
        if not path.exists():
          raise DataPersistenceError(f"File missing: {self.data_dir}")

        with open(path, "r", encoding = "utf-8") as file:
          return json.load(file)
          

        