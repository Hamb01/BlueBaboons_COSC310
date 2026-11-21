"""Factory for sequential, prefixed ids such as r01, m01, k01 and o01.

Coding Notes:
    make_id_generator(prefix) builds a generator for one kind of id.
    The generator looks at the ids that already exist, finds the highest
    number with that prefix, and returns that number + 1.

    We use the highest number rather than len(ids) + 1 because deleting a
    record would make len() hand out an id that is still in use
    (e.g. r01, r03 stored -> len + 1 = r03, a duplicate).

Example:
    new_restaurant_id = make_id_generator("r")
    new_restaurant_id(["r01", "r02"])        -> "r03"
    next_id_in_store(JsonStore(path), "k")   -> next cart id in Carts.json
"""

from typing import Callable, Iterable

from app.repositories.jsonstore import JsonStore

IdGenerator = Callable[[Iterable[str]], str]


def make_id_generator(prefix: str, width: int = 2) -> IdGenerator:
    """
    make_id_generator
    -------------------

    Description:
        Factory that builds an id generator for one prefix

    Args:
        prefix : string -> letters that start every id of this kind ("r", "m", "k", "o")
        width : int -> minimum number of digits, zero padded (2 gives r01; r100 still works)

    Returns:
        IdGenerator -> function that takes the existing ids and returns the next one

    Raises:
        ValueError -> the prefix is empty, contains digits, or width is below 1
    """
    if not prefix or any(char.isdigit() for char in prefix):
        raise ValueError("prefix must be non-empty and contain no digits")
    if width < 1:
        raise ValueError("width must be at least 1")

    def generate(existing_ids: Iterable[str]) -> str:
        numbers = [
            int(item_id[len(prefix):])
            for item_id in existing_ids
            if isinstance(item_id, str)
            and item_id.startswith(prefix)
            and item_id[len(prefix):].isdigit()
        ]
        next_number = max(numbers, default=0) + 1
        return f"{prefix}{next_number:0{width}d}"

    return generate


def next_id_in_store(store: JsonStore, prefix: str, width: int = 2) -> str:
    """
    next_id_in_store
    -------------------

    Description:
        Returns the next free id for a JSON file whose top-level keys are ids
        (Restaurants.json, Carts.json, Orders.json, Users.json)

    Args:
        store : JsonStore -> the store for the file to read
        prefix : string -> the id prefix to count
        width : int -> minimum number of digits

    Returns:
        string -> the next unused id, e.g. "k04"

    Raises:
        DataPersistenceError -> the file could not be read or is not a JSON object
    """
    return make_id_generator(prefix, width)(store.load().keys())
