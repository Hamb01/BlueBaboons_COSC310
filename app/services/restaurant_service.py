import json
import os
import time
from typing import List, Dict, Any, Optional

from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant_schema import RestaurantCreate, RestaurantResponse, RestaurantUpdate

#Coding Notes:

#Local file path is defined as a constant that points towards the master JSON
#Restaurant response is a Pydantic model that inherits from the schemas 
#defined in restaurant_schema.py. It is used to validate the data returned from the repository layer.

#Payload is a dictionary that contains the data for creating or updating the restaurant or menu item. 
# The payload is validated against the Pydantic models before being sent to the repository layer.

#The service layer acts as the buisness controller for the application
#The repository layer  acts as the data access layer
#Our front end is the presentation layer



#From top to bottom :
#list restaurants - returns a list of restaurants based on the search criteria
#get restaurant details - returns the details of a specific restaurant based on its ID
#get all restaurants - returns a list of all restaurants
#create restaurant - creates a new restaurant based on the provided payload
#update restaurant - updates an existing restaurant based on the provided payload
#(menu operations live in menu_service.py)

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
