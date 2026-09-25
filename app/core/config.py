from pathlib import Path
import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Blue Baboons Food Delivery API"
    app_version: str = "0.1.0"
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = base_dir / "data"
    restaurants_file: Path = data_dir / "restaurants.json"

    def __init__(self, **data):
        super().__init__(**data)
        # Allow overriding data directory or file via environment variables
        env_data_dir = os.getenv("DATA_DIR")
        if env_data_dir:
            self.data_dir = Path(env_data_dir)
            self.restaurants_file = self.data_dir / "restaurants.json"

        env_restaurants_file = os.getenv("RESTAURANTS_FILE")
        if env_restaurants_file:
            self.restaurants_file = Path(env_restaurants_file)


def get_settings() -> Settings:
    return Settings()
