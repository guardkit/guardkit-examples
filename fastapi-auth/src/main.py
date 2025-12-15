"""
FastAPI application factory and configuration.

Initializes and configures the FastAPI application with all routers and middleware.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from src.core.config import settings

# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="JWT-based authentication API with user management",
    debug=settings.DEBUG,
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


# Add SlowAPI middleware for rate limiting
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    """Handle rate limit exceeded errors."""
    from fastapi import HTTPException, status

    raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))


app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get(
    "/health",
    status_code=200,
    tags=["health"],
    summary="Health Check",
    description="Check if API is running",
)
async def health_check():
    """Health check endpoint to verify API is running."""
    return {"status": "healthy", "service": settings.APP_NAME}


# Include routers (import here to avoid circular dependencies)
from src.auth.router import router as auth_router

app.include_router(auth_router)


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    print(f"Starting {settings.APP_NAME}")
    print(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    print(f"Shutting down {settings.APP_NAME}")
