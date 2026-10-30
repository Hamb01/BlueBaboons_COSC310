from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health_routes, restaurant_routes, menu_routes
from app.core.config import get_settings
from app.core.exceptions import DomainError, RestaurantNotFoundError, MenuItemNotFoundError, DataPersistenceError 
from schemas.exception_schema import System_Error_Message
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "COSC 310 BILLION VFood-Delivery Application REST API by Team Blue Baboons.\n\n"
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
        "restaurants": "/restaurant",
        "health_check": "/health"
    }

def handle_exceptions(self, exception: DomainError) -> System_Error_Message:
    """Function to map different Exceptions to their respective HTTP status codes"""
    if isinstance(exception, RestaurantNotFoundError):
        exception.status_code = status.HTTP_404_NOT_FOUND
    
    elif isinstance(exception, MenuItemNotFoundError):
        exception.status_code = status.HTTP_404_NOT_FOUND

    elif isinstance(exception, DataPersistenceError):
        exception.status_code = status.HTTP_500_NOT_FOUND

    else:
        exception.status_code = status.HTTP_400_NOT_FOUND

    message = DomainError.model_validate(exception)

    return message
    

# Attach the exception handler method to the app
app.handle_exceptions = handle_exceptions