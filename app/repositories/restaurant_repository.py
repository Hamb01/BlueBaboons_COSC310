import json
from uuid import uuid4
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.exceptions import DomainError, RestaurantNotFoundError, DataPersistenceError, MenuItemNotFoundError
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

  def add_menu_item(self, restaurant_id: str, menu_item: dict) -> Dict[str, Any]:
    """Add a new menu item to the specified restaurant."""
    from app.schemas.menu_item import MenuItem

    repository_data = self.restaurants
    if restaurant_id not in repository_data:
      raise RestaurantNotFoundError(restaurant_id)
    new_menu_item = {
      "id": f"item_{uuid4().hex}",
      "restaurant_id": restaurant_id,
      "name": menu_item.get("name"),
      "price": float(menu_item.get("price", 0.0)),
      "description": menu_item.get("description"),
      "availability": menu_item.get("availability", True),
    }
    new_menu_item = MenuItem.model_validate(new_menu_item).model_dump()
    menu_items = repository_data[restaurant_id].setdefault("menu", [])
    menu_items.append(new_menu_item)
    try:
      self.save_to_file()
    except DataPersistenceError:
      menu_items.pop()
      raise
    return new_menu_item

  def update_menu_item(self, restaurant_id: str, item_id: str, updated_data: dict) -> Dict[str, Any]:
    """Update an existing menu item for the specified restaurant."""
    from app.schemas.menu_item import MenuItem

    repository_data = self.restaurants
    if restaurant_id not in repository_data:
      raise RestaurantNotFoundError(restaurant_id)
    menu_items = repository_data[restaurant_id].get("menu", [])
    target_item = None
    target_index = -1

    for index, item in enumerate(menu_items):
      if item["id"] == item_id and item.get("restaurant_id") == restaurant_id:
        target_item = item
        target_index = index
        break

    if target_item is None:
      raise MenuItemNotFoundError(f"Menu item '{item_id}' was not found.")

    updated_item = {
      "id": item_id,
      "restaurant_id": restaurant_id,
      "name": updated_data.get("name", target_item["name"]),
      "price": float(updated_data.get("price", target_item["price"])),
      "description": updated_data.get("description", target_item["description"]),
      "availability": updated_data.get("availability", target_item["availability"]),
    }
    updated_item = MenuItem.model_validate(updated_item).model_dump()
    repository_data[restaurant_id]["menu"][target_index] = updated_item
    try:
      self.save_to_file()
    except DataPersistenceError:
      menu_items[target_index] = target_item
      raise
    return updated_item
