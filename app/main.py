from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health_routes, restaurant_routes
from app.core.config import get_settings
from app.schemas.restaurantResponse import RestaurantResponse 
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

#just a placeholder to render on localhost:8000/docs                                                                                                                                                                                                            
@app.get("/restaurants", response_model=list[RestaurantResponse], tags=["Restaurants"])                                                                                                              
def sample_restaurants():                                                                                                                                                                                
    return []     

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
