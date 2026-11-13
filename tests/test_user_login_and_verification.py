from pathlib import Path
from fastapi.testclient import TestClient
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user_schema import UserLogin, User, Customer, RestaurantOwner, RestaurantAdmin, Developer, SupportStaff, AccountStatusAndRole

