from pathlib import Path
import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Blue Baboons Food Delivery API"
    app_version: str = "0.1.0"
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = base_dir / "data"

    # Cart and checkout pricing rules (the backend is the only place totals are calculated)
    delivery_fee: float = 2.99
    max_item_quantity: int = 20

    def __init__(self, **data):
        super().__init__(**data)
        # Allow overriding data directory or file via environment variables
        env_data_dir = os.getenv("DATA_DIR")
        if env_data_dir:
            self.data_dir = Path(env_data_dir)
            


def get_settings() -> Settings:
    return Settings()
