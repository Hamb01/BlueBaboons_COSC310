import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.config import get_settings

class RestaurantRepository:
    """Repository layer responsible for reading restaurant data from storage."""

    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or get_settings().restaurants_file

    def get_raw_data(self) -> List[dict[str, Any]]:
        if not self.data_file.exists():
         raise FileNotFoundError(f"File missing: {self.data_file}")

        with open(self.data_file, "r", encoding="utf-8") as file:
           return json.load(file)

        