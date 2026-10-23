from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import (
    auth_routes,
    cart_routes,
    customer_routes,
    health_routes,
    order_routes,
    restaurant_routes,
)
from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, DomainError
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


@app.exception_handler(DomainError)
def handle_domain_error(request: Request, error: DomainError) -> JSONResponse:
    """Single translation point from domain errors to HTTP responses (body matches ErrorResponse)."""
    headers = {"WWW-Authenticate": "Bearer"} if isinstance(error, AuthenticationError) else None
    return JSONResponse(
        status_code=error.status_code,
        content={"error": type(error).__name__, "detail": str(error)},
        headers=headers,
    )


@app.exception_handler(NotImplementedError)
def handle_not_implemented(request: Request, error: NotImplementedError) -> JSONResponse:
    """M2 contract stubs answer 501 until their owner implements them."""
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={"error": "NotImplementedError", "detail": f"Not implemented yet: {error}"},
    )


# Include routers (every M2 router is registered here once, so feature PRs never need to edit this file)
app.include_router(health_routes.router)
app.include_router(restaurant_routes.router)
app.include_router(auth_routes.router)
app.include_router(customer_routes.router)
app.include_router(cart_routes.router)
app.include_router(order_routes.router)

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
