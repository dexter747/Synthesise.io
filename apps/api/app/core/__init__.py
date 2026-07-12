"""
Core module for Synthesize.io API.
Contains configuration, database, security, and utility functions.
"""
from app.core.config import settings
from app.core.database import Base, SessionLocal, get_db, engine
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    verify_access_token,
    verify_refresh_token,
    generate_token,
    hash_token,
    generate_api_key,
)
from app.core.exceptions import (
    SynthesizeException,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    PaymentError,
    ExternalServiceError,
    GenerationError,
)

__all__ = [
    # Config
    "settings",
    # Database
    "Base",
    "SessionLocal",
    "get_db",
    "engine",
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "verify_access_token",
    "verify_refresh_token",
    "generate_token",
    "hash_token",
    "generate_api_key",
    # Exceptions
    "SynthesizeException",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "PaymentError",
    "ExternalServiceError",
    "GenerationError",
]
