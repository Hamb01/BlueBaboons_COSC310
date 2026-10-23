from pathlib import Path
from typing import Any, Dict


class JsonFileStore:
    """Shared load/save helper for repositories that keep a dict of records in one JSON file.

    Records are stored as {"<id>": {...record...}}, the same shape as Restaurants.json.
    Shared by UserRepository, CartRepository and OrderRepository so persistence logic is written once.
    """

    def __init__(self, path: Path):
        self.path = path

    def load(self) -> Dict[str, Any]:
        """Return every record in the file."""
        # TODO: what should happen when the file does not exist yet?
        # TODO: what should happen when the file is corrupted? (Look at RestaurantRepository:
        #       it returns {} on a JSONDecodeError — what does the next save then do to the file?)
        raise NotImplementedError("JsonFileStore.load")

    def save(self, records: Dict[str, Any]) -> None:
        """Write every record to the file."""
        # TODO: what state is the file left in if the app crashes halfway through writing?
        #       Can you make the write all-or-nothing? (search: "atomic file write python os.replace")
        raise NotImplementedError("JsonFileStore.save")

    @staticmethod
    def next_id(records: Dict[str, Any], prefix: str) -> str:
        """Return the next stable ID for a new record, e.g. 'u03'."""
        # TODO: follow the existing 'r01' / 'm01' convention. Must an ID ever be reused after a delete?
        raise NotImplementedError("JsonFileStore.next_id")
