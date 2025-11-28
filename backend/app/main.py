from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from app.core.config import settings
from app.middleware.tenant import TenantMiddleware
from app.api.routes import auth, spaces, reservations, orgs

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    default_response_class=ORJSONResponse,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant middleware
app.add_middleware(TenantMiddleware)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(spaces.router, prefix=f"{settings.API_V1_STR}/spaces", tags=["spaces"])
app.include_router(
    reservations.router,
    prefix=f"{settings.API_V1_STR}/reservations",
    tags=["reservations"]
)
app.include_router(orgs.router, prefix=f"{settings.API_V1_STR}/orgs", tags=["orgs"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print(f"Starting {settings.APP_NAME}...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print(f"Shutting down {settings.APP_NAME}...")
