from pathlib import Path
from typing import Optional
from app.core.config import get_settings


class HealthRepository:
    """Repository layer responsible for checking persistence layer availability."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or get_settings().data_dir

    def check_persistence(self) -> dict[str, str]:
        """Verify data persistence availability."""
        exists = self.data_dir.exists()
        return {
            "status": "connected" if exists else "uninitialized",
            "storage_type": "JSON/CSV"
        }
