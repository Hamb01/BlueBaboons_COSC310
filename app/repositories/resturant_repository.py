from pathlib import Path
from typing import Optional
from app.core.config import get_settings


class ResturantRepository:
    """Checking for resturant information and availability."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir

    def get_resturant_info(self) -> dict[str, str]:
        """Verify resturant information availability."""
        exists = self.data_dir.exists()
        return {
            "resturant_id": get_settings().resturant_id,
            "resturant_name": get_settings().resturant_name,
            "resturant_location": get_settings().resturant_location,
            "resturant_isOpen": get_settings().resturant_isOpen,
            "resturant_cuisine": get_settings().resturant_cuisine
        }
