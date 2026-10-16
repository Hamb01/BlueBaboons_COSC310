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
    self.master_file = self.data_dir / "Restaurants.json"

    self.data_dir.mkdir(parents = True, exist_ok = True)

    if self.master_file.exists():
      try:
        with open(self.master_file, "r", encoding = "utf-8") as file:
          self.restaurants: Dict[str, Any] = json.load(file)
      except json.JSONDecodeError:
        self.restaurants = {}
    else:
      self.restaurants = {}
      self.save_to_file()



  def get_menu_data(self, restaurant_id: str) -> List[Dict[str, Any]]:
    """Read a menu only after resolving its restaurant by stable ID."""
    return self.get_restaurant_data(restaurant_id).get("menu", [])

  def get_restaurant_data(self, id: str = "r01") -> Dict[str, Any]:
    """Method to return restaurant data. can be fed with either the restaurant name or id"""
    if id in self.restaurants:
      return self.restaurants[id]

    for restaurant in self.restaurants.values():
      if restaurant.get("name") == id:
        return restaurant

    raise RestaurantNotFoundError(f"Restaurant doesn't exist: {id}")


  def save_to_file(self):
    try:
      with open(self.master_file, "w", encoding="utf-8") as file:
        json.dump(self.restaurants, file, indent = 4)
    except Exception as e:
      raise DataPersistenceError(f"Error saving to file: {e}")

  def get_all_restaurant(self) -> List[Dict[str, Any]]:
    return list(self.restaurants.values())

  def generate_restaurant_id(self) -> str:
    existing_ids = [int(i[1:]) for i in self.restaurants.keys()
                    if i.startswith("r") and i[1:].isdigit()]
    next_num = max(existing_ids) + 1 if existing_ids else 1
    return f"r{next_num:02d}"

  def create_restaurant(self, restaurant_data: dict) -> Dict[str, Any]:
    #convert to a dict so Pydantic models can be used
    if hasattr(restaurant_data, "model_dump"):
      restaurant_data = restaurant_data.model_dump()

    restaurant_id = self.generate_restaurant_id()
    restaurant_data["id"] = restaurant_id

    self.restaurants[restaurant_id] = restaurant_data
    self.save_to_file()

    return restaurant_data

  def update_restaurant(self, restaurant_id: str, update_data: dict) -> Dict[str, Any]:
    current_data = self.get_restaurant_data(restaurant_id)

    update_dict = update_data.model_dump(exclude_unset = True) if hasattr(update_data,"model_dump") else update_data

    for key, value  in update_dict.items():
      if key == "id":
        continue #Skip attempts to update ID
      current_data[key] = value

    current_data["id"] = restaurant_id

    self.restaurants[restaurant_id] = current_data
    self.save_to_file()

    return current_data
