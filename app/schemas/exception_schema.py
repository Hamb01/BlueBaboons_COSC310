"""Pydantic schema used for serializing the application's custom domain errors."""

from typing import Optional

from pydantic import BaseModel, Field


# pylint: disable=invalid-name
class System_Error_Message(BaseModel):
    """Pydantic model for custom exceptions emitted by the app."""

    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="A quick summary of what went wrong")
    details: Optional[str] = Field(
        default=None,
        description="Additional details that don't need to be included in the summary.",
    )
