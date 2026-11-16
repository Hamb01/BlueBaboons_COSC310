
"""Atomic JSON file storage for the repository layer.

Behaviour:
- load() on a missing file creates it containing {} and returns {}.
- load() on an empty / invalid / non-object file raises DataPersistenceError
and never touches the file on disk.
- save() writes <name>.tmp in the same folder, fsyncs it, then os.replace()s
it onto the target, so the target is always either the old or the new
complete content.
"""

import json
import os
from pathlib import Path
from typing import Any

from app.core.exceptions import DataPersistenceError


class JsonStore:
    def __init__(self, path: str | os.PathLike[str]) -> None:
        self.path = Path(path)

    def load(self) -> dict:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = f.read()
        except FileNotFoundError:
            self.save({})
            return {}
        except OSError as e:
            raise DataPersistenceError(f"Could not read {self.path}: {e}") from e

        if not raw.strip():
            raise DataPersistenceError(f"Data file is empty: {self.path}")

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise DataPersistenceError(f"Invalid JSON in {self.path}: {e}") from e

        if not isinstance(data, dict):
            raise DataPersistenceError(
                f"Expected a JSON object in {self.path}, got {type(data).__name__}"
            )
        return data

    def save(self, data: dict) -> None:
        tmp_path = self.path.with_name(self.path.name + ".tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            # Serialise first so an unserialisable object never leaves a
            # partial temp file behind.
            payload = json.dumps(data, indent=4, ensure_ascii=False)
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(payload)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.path)
        except (OSError, TypeError, ValueError) as e:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise DataPersistenceError(f"Could not save {self.path}: {e}") from e