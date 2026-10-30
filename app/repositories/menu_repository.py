from typing import List, Dict, Any, Optional
from app.core.exceptions import MenuItemNotFoundError
from app.repositories.restaurant_repository import RestaurantRepository

class MenuRepository:
  """Repository layer responsible for reading and writing menu items.

  Menus are stored inside each restaurant record in Restaurants.json, so this repository
  goes through RestaurantRepository instead of opening the file itself.
  """

  def __init__(self, restaurant_repository: Optional[RestaurantRepository] = None):
    self.restaurant_repository = restaurant_repository or RestaurantRepository()

  def get_menu_data(self, restaurant_id: str) -> List[Dict[str, Any]]:
    """Read a menu only after resolving its restaurant by stable ID."""
    return self.restaurant_repository.get_restaurant_data(restaurant_id).get("menu", [])

  def add_menu_item(self, restaurant_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
    """Append a new, already validated item to a restaurant's menu and save it."""
    restaurant = self.restaurant_repository.get_restaurant_data(restaurant_id)
    restaurant.setdefault("menu", []).append(item_data)
    self.restaurant_repository.save_to_file()
    return item_data

  def update_menu_item(self, restaurant_id: str, item_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
    """Replace the fields of one existing item in place and save it. The item's ids never change."""
    
    restaurant_data = self.restaurant_repository.get_restaurant_data(restaurant_id)
    if "menu" not in restaurant_data or not restaurant_data["menu"]:
          raise MenuItemNotFoundError("Restaurant has no menu items.")
        
    item = self._find_item(restaurant_id, item_id)
    for key, value in item_data.items():
      if key not in ("id", "restaurant_id"):
        item[key] = value
    self.restaurant_repository.save_to_file()
    return item
    

  def remove_menu_item(self, restaurant_id: str, item_id: str) -> None:
    """Delete one item from a restaurant's menu and save it."""
    menu = self.get_menu_data(restaurant_id)
    menu.remove(self._find_item(restaurant_id, item_id))
    self.restaurant_repository.save_to_file()

  def generate_menu_item_id(self) -> str:
    """Return the next menu item id. Ids are unique across every restaurant, not per restaurant."""
    existing_ids = []
    for restaurant in self.restaurant_repository.get_all_restaurant():
      for item in restaurant.get("menu", []):
        item_id = item.get("id", "")
        if isinstance(item_id, str) and item_id.startswith("m") and item_id[1:].isdigit():
          existing_ids.append(int(item_id[1:]))
    next_num = max(existing_ids) + 1 if existing_ids else 1
    return f"m{next_num:02d}"

  def _find_item(self, restaurant_id: str, item_id: str) -> Dict[str, Any]:
    for item in self.get_menu_data(restaurant_id):
      if item.get("id") == item_id:
        return item
    raise MenuItemNotFoundError(f"Menu item '{item_id}' was not found.")
