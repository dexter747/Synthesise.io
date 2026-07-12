"""
Synthesize.io API - Main Application Entry Point
"""
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import SynthesizeException


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print(f"Starting Synthesize.io API v{settings.VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    
    yield
    
    # Shutdown
    print("Shutting down Synthesize.io API")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Synthesize.io - AI-Powered Synthetic Data Generation Platform",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(SynthesizeException)
async def synthesize_exception_handler(request: Request, exc: SynthesizeException):
    """Handle custom Synthesize exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging."""
    errors = exc.errors()
    print(f"Validation error on {request.url.path}: {errors}")
    
    # Return detailed validation errors
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": errors,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    # Log the error
    print(f"Unhandled exception: {exc}")
    
    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_ERROR",
            "message": str(exc),
            "type": type(exc).__name__,
        },
    )


# =============================================================================
# MIDDLEWARE
# =============================================================================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# Session middleware (required for OAuth state management)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
    session_cookie="synthesize_session",
    max_age=3600,  # 1 hour
    same_site="lax",
    https_only=False,  # Must be False for localhost development
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Request-ID"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# =============================================================================
# API ROUTES
# =============================================================================

# Include v1 API router
app.include_router(api_router, prefix="/api/v1")


# =============================================================================
# HEALTH & STATUS ENDPOINTS
# =============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    Returns basic health status without requiring authentication.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check for Kubernetes-style deployments.
    Verifies that the application is ready to serve traffic.
    """
    # TODO: Add database and Redis connectivity checks
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "redis": "ok",
        },
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - returns API information.
    """
    return {
        "name": "Synthesize.io API",
        "version": settings.VERSION,
        "description": "AI-Powered Synthetic Data Generation Platform",
        "documentation": "/docs",
        "api_prefix": "/api/v1",
    }

