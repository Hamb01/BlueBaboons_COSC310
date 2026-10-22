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

  def update_menu_item(self, restaurant_id: str, item_id: str, updated_data: Dict[str, Any], make_new: bool = False) -> Dict[str, Any]:

    restaurant = self.restaurants.get(restaurant_id)
    existing_menu = restaurant.get("menu", [])

    if existing_menu :
      # we are updating an existing menu item
      new_menu_item = {
        "id" : item_id,
        "restaurant_id" : restaurant_id,
        "name" : updated_data.get("name", existing_menu["name"]),
        "description" : updated_data.get("description", existing_menu["description"]),
        "price" : updated_data.get("price", existing_menu["price"]),
        "availability" : updated_data.get("availability", existing_menu["availability"])
        }
    elif make_new:
      # we are creating a new menu item
      new_menu_item = {
              "id" : self.generate_menu_item_id(restaurant_id),
              "restaurant_id" : restaurant_id,
              "name" : updated_data.get("name", "no item"),
              "description" : updated_data.get("description", "no description"),
              "price" : updated_data.get("price", 0.0),
              "availability" : updated_data.get("availability", False)
              }
    else:
      # error (no such menu item)
      return {}
    
    restaurant["menu"].append(new_menu_item)
    self.restaurants[restaurant_id]["menu"] = restaurant["menu"]
      
    self.save_to_file()

    return new_menu_item

  def remove_menu_item(self, restaurant_id: str, item_id: str):
    menu = self.restaurants[restaurant_id].get("menu", [])
   
    for item in menu:
      if item["id"] == item_id:
        menu.pop(item)

    self.restaurants[restaurant_id]["menu"] = menu

    self.save_to_file()
    
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

  def generate_menu_item_id(self, restaurant_id: str) -> str:
    menu = self.restaurants[restaurant_id].get("menu", [])
    existing_ids = []
    for item in menu:
      item_id = item.get("id", "")
      if isinstance(item_id, str) and item_id.startswith("m") and item_id[1:].isdigit():
        existing_ids.append(int(item_id[1:]))
    next_num = max(existing_ids) + 1 if existing_ids else 1
    return f"m{next_num:02d}"

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
