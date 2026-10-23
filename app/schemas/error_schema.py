from typing import Any, Dict

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Body returned for every domain error, so clients can handle failures consistently."""
    # TODO: what should every error response contain so the frontend (and a TA using /docs) can understand it?
    pass


def error_responses(*status_codes: int) -> Dict[int | str, Dict[str, Any]]:
    """Build the `responses=` argument for a route so OpenAPI documents its error responses.

    Intended usage: @router.get("/cart", responses=error_responses(401, 403))
    """
    # TODO: look up FastAPI's "Additional Responses in OpenAPI" docs and return the dict it expects.
    return {}
