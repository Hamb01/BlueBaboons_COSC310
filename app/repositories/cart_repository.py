from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.repositories.json_file_store import JsonFileStore


class CartRepository:
    """Repository layer for shopping carts.

    Owner: Person B (cart).
    Storage: data/Carts.json
    TODO: what does one stored cart look like?
    TODO: should a stored cart line keep the item's name and price, or only a reference to it?
          What happens to stored prices when a restaurant changes its menu?
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir
        self.store = JsonFileStore(self.data_dir / "Carts.json")

    def get_active_for_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("CartRepository.get_active_for_customer")

    def create(self, customer_id: str) -> Dict[str, Any]:
        raise NotImplementedError("CartRepository.create")

    def save(self, cart: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("CartRepository.save")
