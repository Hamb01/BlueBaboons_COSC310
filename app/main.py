"""FastAPI app configuration and global exception handling for the Blue Baboons API."""

import logging
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from app.api.routes import health_routes, menu_routes, restaurant_routes
from app.core.config import get_settings
from app.core.exceptions import (
    DataPersistenceError,
    DomainError,
    EmptyMenuError,
    MenuItemNotFoundError,
    RestaurantNotFoundError,
    UserAuthentificationError,
    UserNotAuthorizedError
)
from app.schemas.exception_schema import System_Error_Message

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "COSC 310 VFood-Delivery Application REST API by Team Blue Baboons.\n\n"
        "Foundation setup providing service health verification and OpenAPI "
        "documentation."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Enable CORS for local development and frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_routes.router)
app.include_router(restaurant_routes.router)
app.include_router(menu_routes.router)

# Serve the frontend alongside the REST API (also included in the Docker image).
app.mount(
    "/ui",
    StaticFiles(directory=Path(__file__).resolve().parent / "frontend", html=True),
    name="frontend",
)


@app.get("/", tags=["Root"], summary="API Root Overview")
def root_overview():
    """Return links to the service documentation and core endpoints."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "documentation": "/docs",
        "restaurants": "/restaurants",
        "health_check": "/health",
    }


# Create a simple logger to keep track of errors that arise while using the system
log_file = settings.base_dir / "docs" / "ErrorLog.log"
log_file.parent.mkdir(parents=True, exist_ok=True)
log_file.touch(exist_ok=True)
logging.basicConfig(filename=str(log_file))
error_logger = logging.getLogger(__name__)


@app.exception_handler(DomainError)
def handle_application_domain_exceptions(
    _request: Request, exception: DomainError
) -> JSONResponse:
    """Map domain exceptions to their corresponding HTTP responses."""
    if isinstance(exception, UserAuthentificationError):
        exception.status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exception, UserNotAuthorizedError):
        exception.status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exception, (RestaurantNotFoundError, MenuItemNotFoundError, EmptyMenuError)):
        exception.status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exception, DataPersistenceError):
        exception.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        exception.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if not exception.message:
            exception.message = "An unknown error occurred"
        exception.details = f"{exception.details} Exception is not properly caught"

    error_message = System_Error_Message.model_validate(
        {
            "status_code": exception.status_code,
            "message": exception.message,
            "details": exception.details,
        }
    )

    error_logger.error(
        "Status code: %s, Message: %s, Details: %s",
        error_message.status_code,
        error_message.message,
        error_message.details,
    )

    return JSONResponse(
        status_code=error_message.status_code,
        content={
            "status_code": error_message.status_code,
            "message": error_message.message,
            "details": error_message.details,
        },
    )


@app.exception_handler(ValidationError)
def handle_system_exceptions(_request: Request, exception: ValidationError) -> JSONResponse:
    """Handle request-validation failures for Pydantic models."""
    error_logger.error(
        "Status code: %s, Message: %s errors when validating model, Details: %s",
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        exception.error_count,
        str(exception),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": f"{exception.error_count} errors when validating model",
            "details": str(exception),
        },
    )
