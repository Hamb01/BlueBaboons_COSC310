from pydantic import BaseModel, Field
from typing import Optional


class System_Error_Message(BaseModel):
    """Pydantic model for all of the custom exceptions we define for our system"""
    status_code: int = Field(..., description="HTTP status code")
    description: str = Field(..., description="Error Message")
    details: Optional[str] = Field(None, description="Additional details")