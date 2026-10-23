from typing import Any, Dict

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Body returned for every DomainError (see the handler in app/main.py)."""
    error: str = Field(..., description="Name of the domain error, e.g. 'MixedRestaurantCartError'")
    detail: str = Field(..., description="Human-readable explanation of what went wrong")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "MenuItemUnavailableError",
                "detail": "Menu item 'm02' is currently unavailable.",
            }
        }
    }


_DESCRIPTIONS = {
    400: "Bad request",
    401: "Missing or invalid bearer token",
    403: "Authenticated, but not allowed to perform this operation",
    404: "Resource not found",
    409: "Request conflicts with the current state",
    422: "Request failed validation",
    500: "Data persistence failure",
    501: "Endpoint is part of the M2 contract but not implemented yet",
}


def error_responses(*status_codes: int) -> Dict[int | str, Dict[str, Any]]:
    """Build the `responses=` argument for a route so OpenAPI documents its errors.

    Usage: @router.get("/cart", responses=error_responses(401, 403))
    """
    return {
        code: {"model": ErrorResponse, "description": _DESCRIPTIONS.get(code, "Error")}
        for code in status_codes
    }
