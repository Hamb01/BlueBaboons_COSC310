import os

from pydantic import json
import json
import time

from app.core.config import get_settings
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant_schema import RestaurantResponse


#Constants

LOCAL_FILE_PATH = "app/data/restaurant_data.json"


class RestaurantService:
    """Service layer coordinating application health and storage verification."""

    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def get_restaurant_status(self) -> RestaurantResponse:
        information = self.repository.get_restaurant_data();

        return RestaurantResponse(
            id = information.get("restaurant_id"),
            name = information.get("restaurant_name"),
            location = information.get("restaurant_location"),
            isOpen = information.get("restaurant_isOpen"),
            cuisine = information.get("restaurant_cuisine")
        )
    def add_new_menu_item(self, restaurant_id: str, menu_item: dict) -> dict:
        """Add a new menu item to the specified restaurant."""
        repository_data = {}

        if os.path.exists(LOCAL_FILE_PATH):
            try:
                with open(LOCAL_FILE_PATH, "r") as file:
                    repository_data = json.load(file)
            except json.JSONDecodeError:
                repository_data = {}
        if restaurant_id not in repository_data:
            repository_data[restaurant_id] = {"menu": []}
            #Grabs all the shit from the dictionary extracted from the user and adds it to the menu list
        new_menu_item ={
            #Grabs a unique ID from the current time in seconds
            "id": f"item_{int(time.time())}",
            "name": menu_item.get("name"),
            "price": float(menu_item.get("price", 0.0)),
            "description": menu_item.get("description"),
            "category": menu_item.get("category", "Uncategorized")
        }
    def update_menu_item(self, restaurant_id: str, item_id: str, updated_data: dict, littleBit: bool = False) -> dict:
        """Update an existing menu item for the specified restaurant."""
        if not os.path.exists(LOCAL_FILE_PATH):
            raise FileNotFoundError("Restaurant data file not found.")
        with open(LOCAL_FILE_PATH, "r") as file:
            repository_data = json.load(file)
        if restaurant_id not in repository_data:
            raise ValueError(f"Error 404: Restaurant not found.")
        menu_items = repository_data[restaurant_id].get("menu", [])
        target_item = None
        target_index = -1

        if target_item is None:
            raise ValueError(f"Error 404: Menu item not found.")

        if littleBit:
             updated_item = {
                 "id": item_id,
                 "name": updated_data.get("name", target_item["name"]),
                 "price": float(updated_data.get("price", target_item["price"])) if "price" in updated_data else target_item.get("price"),
                 "description": updated_data.get("description", target_item["description"]),
                 "category": updated_data.get("category", target_item["category"])
             }
        else:
            updated_item = {
                "id": item_id,
                "name": updated_data.get("name", target_item["name"]),
                "price": float(updated_data.get("price", 0.0)),
                "description": updated_data.get("description", target_item["description"]),
                "category": updated_data.get("category", target_item["category"])
            }
        repository_data[restaurant_id]["menu"][target_index] = updated_item
       
        with open(LOCAL_FILE_PATH, "w") as file:
            json.dump(repository_data, file, indent=2)

        print(f"Menu Item Updated! Code: 200")
        #Appends the menu item to the restaurant's menu list
        repository_data[restaurant_id]["menu"].append(updated_item)
        with open(LOCAL_FILE_PATH, "w") as file:
            json.dump(repository_data, file, indent=2)
        return updated_item