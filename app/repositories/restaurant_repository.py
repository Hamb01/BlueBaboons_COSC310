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

    with open(self.data_dir / "Restaurant_Names.json", "r", encoding="utf-8") as file:
      # Key:   Restaurant id
      # Value: Restaurant_Name.json
      self.restaurant_names = json.load(file)

    with open(self.data_dir / "Restaurant_Keys.json", "r", encoding="utf-8") as file:
      # Key:   Restaurant_Name
      # Value: Restaurant id
      self.restaurant_keys = json.load(file)


  def get_menu_data(self, restaurant_id: str) -> List[Dict[str, Any]]:
    """Read a menu only after resolving its restaurant by stable ID."""
    if restaurant_id not in self.restaurant_names:
      raise RestaurantNotFoundError(restaurant_id)
    return self.get_restaurant_data(restaurant_id).get("menu", [])

  def get_restaurant_data(self, id: str = "r01") -> Dict[str, Any]:
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
    
  def save_mappings(self):
    with open(self.names_file, "w", encoding="utf-8") as file:
      json.dump(self.restaurant_names, file, indent = 4)
    with open(self.keys_file, "w", encoding="utf-8") as file:
      json.dump(self.restaurant_keys, file, indent = 4)
          
  def get_all_restaurant(self) -> List[Dict[str, Any]]:
    restaurants = []
    for id in self.restaurant_names.keys():
      try:
        restaurant_data = self.get_restaurant_data(id)
        restaurants.append(restaurant_data)
      except RestaurantNotFoundError:
        continue
    return restaurants

  def generate_restaurant_id(self) -> str:
    existing_ids = [int(i[1:]) for i in self.restaurant_names.keys() 
                    if i.startswith("r") and i[1:].isdigit()]
    next_num = max(existing_ids) + 1 if existing_ids else 1
    return f"r{next_num:02d}"
      
  def create_restaurant(self, restaurant_data: dict) -> Dict[str, Any]:
    restaurant_id = self.generate_restaurant_id()
    restaurant_data["id"] = restaurant_id
    restaurant_name = restaurant_data.get("name")
    baseName = f"restaurant{restaurant_id}"
    
    self.restaurant_names[restaurant_id] = baseName
    if restaurant_name:
      self.restaurant_keys[restaurant_name] = restaurant_id
      
      self._save_mappings()
      
      restaurants_dir = self.data_dir / "restaurants"
      restaurants_dir.mkdir(parents=True, exist_ok=True)
      file_path = restaurants_dir / f"{baseName}.json"
      
      with open(file_path, "w", encoding="utf-8") as file:
        json.dump(restaurant_data, file, ensure_ascii=False, indent=4)
        
        return restaurant_data

  def update_restaurant(self, restaurant_id: str, update_data: dict) -> Dict[str, Any]:
    current_data = self.get_restaurant_data(restaurant_id)
    
    update_dict = update_data.model_dump(exclude_unset = True) if hasattr(updated_data,"model_dump") else update_data
    
    name_old = current_data.get("name")
    name_new = update_dict.get("name")
    
    for key, value in update_dict.items():
      if name_old in self.restaurant_keys:
        del self.restaurant_keys[name_old]
      self.restaurant_keys[name_new] = restaurant_id
      self.save_mappings()
      
    file_name = self.restaurant_names.get(restaurant_id) + ".json"
    file_path = self.data_dir / "restaurants" / file_name
    
    with open (file_path, "w", encoding = "utf-8") as file:
      json.dump(current_data, file, indent = 4)
      
    return current_data
    
  
  
                                                                        
    
    
    
  
         