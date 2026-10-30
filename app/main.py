from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import ValidationError

from app.api.routes import health_routes, restaurant_routes, menu_routes
from app.core.config import get_settings
from app.schemas.exception_schema import System_Error_Message
from app.core.exceptions import (
    DomainError, 
    RestaurantNotFoundError, 
    MenuItemNotFoundError,
    EmptyMenuError, 
    DataPersistenceError
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "COSC 310 VFood-Delivery Application REST API by Team Blue Baboons.\n\n"
        "Foundation setup providing service health verification and OpenAPI documentation."
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
app.mount("/ui", StaticFiles(directory=Path(__file__).resolve().parent / "frontend", html=True), name="frontend")

@app.get("/", tags=["Root"], summary="API Root Overview")
def root_overview():
    """Welcome endpoint providing links to documentation and health status."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "documentation": "/docs",
        "restaurants": "/restaurants",
        "health_check": "/health"
    }

# Create A simple logger to keep track of errors that arise while using the system
log_file = settings.data_dir / "ErrorLog.log"
log_file.touch(exist_ok=True)
logging.basicConfig(filename=log_file)
error_logger = logging.getLogger(__name__)

@app.exception_handler(DomainError)
def handle_application_domain_exceptions(request: Request, exception: DomainError) -> JSONResponse:
    """Function to map different Exceptions to their respective HTTP status codes"""
    
    if isinstance(exception, RestaurantNotFoundError):
        exception.status_code = status.HTTP_404_NOT_FOUND
    
    elif isinstance(exception, MenuItemNotFoundError):
        exception.status_code = status.HTTP_404_NOT_FOUND

    elif isinstance(exception, EmptyMenuError):
        exception.status_code = status.HTTP_404_NOT_FOUND

    elif isinstance(exception, DataPersistenceError):
        exception.status_code = status.HTTP_500_NOT_FOUND

    else:
        exception.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        exception.details += "Exception is not properly caught"



    error_message = System_Error_Message.model_validate({"status_code" : exception.status_code, 
                                                         "message" : exception.message, 
                                                         "details" : exception.details})
    
    error_logger.exception(f"""Status code: {error_message.status_code}, 
                                Message: {error_message.message}, 
                                Details: {error_message.details}""")

    return JSONResponse(
        status_code=error_message.status_code,
        content={"message": error_message.message, "details": error_message.details}
    )

@app.exception_handler(ValidationError)
def handle_system_exceptions(request: Request, exception: ValidationError):
    """Function to handle and log errors arising from botched pydantic model validations"""

    return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"message": f"{exception.error_count} errors when validating model", "details": str(exception)}
        )
