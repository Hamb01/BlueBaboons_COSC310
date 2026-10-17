import json
import os
import time

from app.core.exceptions import MenuItemNotFoundError
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.menu_item import MenuItem
from app.schemas.restaurant_schema import RestaurantCreate, RestaurantResponse, RestaurantUpdate



#Constants

LOCAL_FILE_PATH = "app/data/restaurant_data.json"


class RestaurantService:
    """Service layer coordinating application health and storage verification."""

    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def get_restaurant_status(self) -> RestaurantResponse:
        information = self.repository.get_restaurant_data();

        return RestaurantResponse.model_validate(information)

    def list_restaurants(
        self,
        search: str | None = None,
        cuisine: str | None = None,
        location: str | None = None,
        is_open: bool | None = None,
    ) -> list[RestaurantResponse]:
        if search is None:
            search = ""
        if cuisine is None:
            cuisine = ""
        if location is None:
            location = ""

        # Remove surrounding spaces and ignore capitalization when comparing.
        search = search.strip().casefold()
        cuisine = cuisine.strip().casefold()
        location = location.strip().casefold()

        matching_restaurants = []
        all_restaurants = self.repository.get_all_restaurant()

        for data in all_restaurants:
            restaurant = RestaurantResponse.model_validate(data)
            restaurant_name = restaurant.name.casefold()
            restaurant_cuisine = restaurant.cuisine.casefold()
            restaurant_location = restaurant.location.casefold()

            # Skip this restaurant if the search text matches none of its fields.
            if search != "":
                matches_name = search in restaurant_name
                matches_cuisine = search in restaurant_cuisine
                matches_location = search in restaurant_location

                if not (matches_name or matches_cuisine or matches_location):
                    continue

            if cuisine != "":
                if restaurant_cuisine != cuisine:
                    continue

            if location != "":
                if location not in restaurant_location:
                    continue

            if is_open is not None:
                if restaurant.isOpen != is_open:
                    continue
            matching_restaurants.append(restaurant)

        return matching_restaurants

    def get_restaurant_details(self, restaurant_id: str) -> RestaurantResponse:
        information = self.repository.get_restaurant_data(restaurant_id)
        return RestaurantResponse.model_validate(information)

    def get_all_restaurants(self) -> list[RestaurantResponse]:
        restaurants_data = self.repository.get_all_restaurant()
        return [RestaurantResponse.model_validate(item) for item in restaurants_data]


    def create_restaurant(self, payload: RestaurantCreate) -> RestaurantResponse:
        information = self.repository.create_restaurant(payload)
        return RestaurantResponse.model_validate(information)

    def update_restaurant(
        self, restaurant_id: str, payload: RestaurantUpdate
    ) -> RestaurantResponse:
        information = self.repository.update_restaurant(restaurant_id, payload)
        return RestaurantResponse.model_validate(information)

    def get_menu(self, restaurant_id: str) -> list[MenuItem]:
        return [
            MenuItem.model_validate(item)
            for item in self.repository.get_menu_data(restaurant_id)
            if item.get("restaurant_id") == restaurant_id
        ]

    def get_menu_item(self, restaurant_id: str, item_id: str) -> MenuItem:
        for item in self.get_menu(restaurant_id):
            if item.id == item_id:
                return item
        raise MenuItemNotFoundError(f"Menu item '{item_id}' was not found.")

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
