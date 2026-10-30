from pydantic import BaseModel, Field
from typing import Optional


class System_Error_Message(BaseModel):
    """Pydantic model for all of the custom exceptions we define for our system"""
    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="a quick summary of what went wrong")
    details: Optional[str] = Field(None, description="Additional details that don't need to be included in the summary of the error")