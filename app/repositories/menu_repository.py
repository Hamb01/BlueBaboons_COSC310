from typing import List, Dict, Any, Optional
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

  def update_menu_item(self, restaurant_id: str, item_id: str, updated_data: Dict[str, Any], make_new: bool = False) -> Dict[str, Any]:

    restaurants = self.restaurant_repository.restaurants
    restaurant = restaurants.get(restaurant_id)
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
    restaurants[restaurant_id]["menu"] = restaurant["menu"]

    self.restaurant_repository.save_to_file()

    return new_menu_item

  def remove_menu_item(self, restaurant_id: str, item_id: str):
    restaurants = self.restaurant_repository.restaurants
    menu = restaurants[restaurant_id].get("menu", [])

    for item in menu:
      if item["id"] == item_id:
        menu.pop(item)

    restaurants[restaurant_id]["menu"] = menu

    self.restaurant_repository.save_to_file()

  def generate_menu_item_id(self, restaurant_id: str) -> str:
    menu = self.restaurant_repository.restaurants[restaurant_id].get("menu", [])
    existing_ids = []
    for item in menu:
      item_id = item.get("id", "")
      if isinstance(item_id, str) and item_id.startswith("m") and item_id[1:].isdigit():
        existing_ids.append(int(item_id[1:]))
    next_num = max(existing_ids) + 1 if existing_ids else 1
    return f"m{next_num:02d}"
