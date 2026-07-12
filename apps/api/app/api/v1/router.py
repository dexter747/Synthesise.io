"""
API v1 Router - aggregates all endpoint modules.
"""
from fastapi import APIRouter
from app.core.config import settings

from app.api.v1.endpoints import (
    auth,
    users,
    datasets,
    jobs,
    admin,
    organizations,
    subscriptions,
    api_keys,
    webhooks,
    payments,
    queries,
    usage,
    data_factory,
)


api_router = APIRouter()

# Health check endpoint
@api_router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for the API v1."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }

# Authentication routes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# User management routes
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

# Dataset routes
api_router.include_router(
    datasets.router,
    prefix="/datasets",
    tags=["Datasets"],
)

# Generation job routes
api_router.include_router(
    jobs.router,
    prefix="/jobs",
    tags=["Jobs"],
)

# Organization routes
api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["Organizations"],
)

# Subscription & billing routes
api_router.include_router(
    subscriptions.router,
    prefix="/subscriptions",
    tags=["Subscriptions"],
)

# API key management routes
api_router.include_router(
    api_keys.router,
    prefix="/api-keys",
    tags=["API Keys"],
)

# Webhook routes
api_router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["Webhooks"],
)

# Payment routes
api_router.include_router(
    payments.router,
    prefix="/payments",
    tags=["Payments"],
)

# Usage & quota routes
api_router.include_router(
    usage.router,
    prefix="/usage",
    tags=["Usage & Quotas"],
)

# Admin routes (requires admin role)
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"],
)

# Customer query routes (public submit + admin management)
api_router.include_router(
    queries.router,
    prefix="/queries",
    tags=["Contact Queries"],
)

# Data Factory routes (synthetic data generation)
api_router.include_router(
    data_factory.router,
    prefix="/data-factory",
    tags=["Data Factory"],
)
