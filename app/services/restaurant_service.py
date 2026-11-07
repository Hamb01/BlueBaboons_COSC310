"""Service layer coordinating restaurant business logic for the API."""

# Coding Notes:
# The service layer acts as the business controller for the application.
# The repository layer acts as the data access layer.
# Our frontend is the presentation layer.
#
# From top to bottom:
# - list restaurants
# - get restaurant details
# - get all restaurants
# - create restaurant
# - update restaurant
# - menu operations live in menu_service.py

from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant_schema import RestaurantCreate, RestaurantResponse, RestaurantUpdate


class RestaurantService:
    """Service layer coordinates restaurant business logic."""

    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def list_restaurants(
        self,
        search: str | None = None,
        cuisine: str | None = None,
        location: str | None = None,
        is_open: bool | None = None,
    ) -> list[RestaurantResponse]:
        """
        list_restaurants
        -----------------

        Description:
            Returns data for all restaurants that match the the provided search criteria (or all restaurants if no search criteria is provided)
        
        Args:
            search   : string (optional) -> Restaurant name, cuisine or location of the restaurant[s] you wish to retrieve
            cuisine  : string (optional) -> Cuisine type for the restaurants you wish to retrieve
            location : string (optional) -> Location of the restaurants you wish to retrieve
            is_open  : string (optional) -> Select if you wish to have restaurants that are closed returned

        Returns:
            matching_restaurants : List -> All restaurants that match your search parameters

        Raises:
            none ***BUG : This should have some kind of check to verify the data exists***
        
        """
        if search is None:
            search = ""
        if cuisine is None:
            cuisine = ""
        if location is None:
            location = ""

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

            if search != "":
                matches_name = search in restaurant_name
                matches_cuisine = search in restaurant_cuisine
                matches_location = search in restaurant_location

                if not (matches_name or matches_cuisine or matches_location):
                    continue

            if cuisine != "" and cuisine not in ("", restaurant_cuisine):
                continue

            if location != "" and location not in restaurant_location:
                continue

            if is_open is not None and restaurant.isOpen != is_open:
                continue

            matching_restaurants.append(restaurant)

        return matching_restaurants

    def get_restaurant_details(self, restaurant_id: str) -> RestaurantResponse:
        """
        get_restaurant_details
        ------------------------

        Description:
            Returns the data pertaining to one specific restaurant
        
        Args:
            restaurant_id : string -> unique ID belonging to the restaurant in question

        Returns:
            RestaurantResponse -> Data related to the restaurant (documented in the restaurant schemas) 

        Raises:
            ValidationError -> The data stored in the restaurant respository is of the wrong shape ***BUG : This will return 422, but it should return 500 ***
            RestaurantNotFoundError -> The restaurant is not stored in the restaurants.json file (raised by self.repository.get_restaurant_data(restaurant_id))
        """
        information = self.repository.get_restaurant_data(restaurant_id)
        return RestaurantResponse.model_validate(information)

    def get_all_restaurants(self) -> list[RestaurantResponse]:
        """
        get_all_restaurants
        -------------------

        Description:
            returns a list of all restaurants currently stored in the system

        Args: 
            none

        Returns:
            Restaurant_data : List -> List of all restaurants currently stored in the system (each restaurant is stored as a dictionary)

        Raises: 
            ValidationError -> The data stored in the restaurant respository is of the wrong shape ***BUG : This will return 422, but it should return 500 ***
        """
        restaurants_data = self.repository.get_all_restaurant()
        return [RestaurantResponse.model_validate(item) for item in restaurants_data]

    def create_restaurant(self, payload: RestaurantCreate) -> RestaurantResponse:
        """
        create_restaurant
        -------------------

        Description:
            Creates a new restaurant and returns the stored version

        Args: 
            payload : RestaurantCreate -> Dictionary of all the information required to create a restaurant

        Returns:
            RestaurantResponse -> all data pertaining to the restaurant (defined in Restaurant_Schemas)

        Raises: 
            ValidationError -> The data stored in the restaurant respository is of the wrong shape ***BUG : This will return 422, but it should return 500 ***
            DataPersistenceError -> There was an error while adding the new restaurant to the JSON (Raised by restaurant_repository.save_to_file())
        """
        information = self.repository.create_restaurant(payload.model_dump())
        return RestaurantResponse.model_validate(information)

    def update_restaurant(
        self,
        restaurant_id: str,
        payload: RestaurantUpdate,
    ) -> RestaurantResponse:
        """
        update_restaurant
        -------------------

        Description:
            Update some of the information related to a restaurant.
            This edits the data without completely replacing the restaurant

        Args: 
            restaurant_id : string -> unique ID belonging to the restaurant in question
            payload : RestaurantUpdate -> the data field(s) to be updated

        Returns:
            RestaurantResponse -> All the data of the updated restaurant

        Raises: 
            RestaurantNotFoundError -> The restaurant is not stored in the restaurants.json file (raised by self.repository.get_restaurant_data(restaurant_id))
            DataPersistenceError -> There was an error while adding the new restaurant to the JSON (Raised by restaurant_repository.save_to_file())
            ValidationError -> The data stored in the restaurant respository is of the wrong shape ***BUG : This will return 422, but it should return 500 ***
        """
        information = self.repository.update_restaurant(
            restaurant_id,
            payload.model_dump(exclude_unset=True),
        )
        return RestaurantResponse.model_validate(information)
