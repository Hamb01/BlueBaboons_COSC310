from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Application health status")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="API version")
    persistence: str = Field(default="connected", description="Persistence layer status")
