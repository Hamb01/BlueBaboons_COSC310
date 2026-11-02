from typing import List, Dict, Any, Optional
from app.core.exceptions import MenuItemNotFoundError, EmptyMenuError, RestaurantNotFoundError
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



  def add_menu_item(self, restaurant_id: str, menu_item: Dict[str, Any]):
    """Add a new Menu item onto a specific menu"""

    restaurants = self.restaurant_repository.restaurants
    restaurant_menu = restaurants.get(restaurant_id).get("menu")

    # Create a menu if one does not exist
    if not restaurant_menu:
      restaurant_menu = []
    
    restaurant_menu.append(menu_item) 
    restaurants[restaurant_id]["menu"] = restaurant_menu

    self.restaurant_repository.save_to_file()
    return menu_item

    
  def update_menu_item(self, restaurant_id: str, item_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
    """Replace the fields of one existing item in place and save it. The item's ids never change."""
    
    restaurant_data = self.restaurant_repository.get_restaurant_data(restaurant_id)

    if not restaurant_data["menu"]:
      raise EmptyMenuError(restaurant_id)
    
    if "menu" not in restaurant_data:
      raise MenuItemNotFoundError(restaurant_id, item_id)
        
    item = self._find_item(restaurant_id, item_id)
    for key, value in item_data.items():
      if key not in ("id", "restaurant_id"):
        item[key] = value
    self.restaurant_repository.save_to_file()
    return item

  def remove_menu_item(self, restaurant_id: str, item_id: str):
    restaurants = self.restaurant_repository.restaurants
    
    try:
      menu = restaurants[restaurant_id].get("menu", [])
    except KeyError as e:
      raise RestaurantNotFoundError(restaurant_id)

    itemNotFound = True
    for item in menu:
      if item["id"] == item_id:
        menu.remove(item)
        itemNotFound = False

    if itemNotFound:
      raise MenuItemNotFoundError(restaurant_id, item_id)

    restaurants[restaurant_id]["menu"] = menu

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
    raise MenuItemNotFoundError(restaurant_id, item_id)
