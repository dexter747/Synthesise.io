"""
Security utilities for Synthesize.io API.
Handles password hashing, JWT tokens, and authentication.
"""
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Any, Union

import bcrypt
from jose import jwt, JWTError
from pydantic import ValidationError

from app.core.config import settings


# =============================================================================
# PASSWORD HASHING
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    # Truncate to 72 bytes for bcrypt compatibility
    password_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))


def hash_password(password: str) -> str:
    """Generate password hash."""
    # Truncate to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


# =============================================================================
# TOKEN GENERATION
# =============================================================================

def generate_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """Hash a token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_api_key() -> Tuple[str, str, str]:
    """
    Generate an API key with prefix, full key, and hash.
    Returns: (prefix, full_key, key_hash)
    """
    prefix = "sk_" + ("live_" if settings.ENVIRONMENT == "production" else "test_")
    key = secrets.token_urlsafe(32)
    full_key = prefix + key
    key_hash = hash_token(full_key)
    return prefix[:8], full_key, key_hash


# =============================================================================
# JWT TOKENS
# =============================================================================

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Optional custom expiration time
        additional_claims: Additional claims to include in token
    
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "sub": str(subject),
        "type": "access",
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT refresh token
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "sub": str(subject),
        "type": "refresh",
        "jti": secrets.token_urlsafe(16),  # Unique token ID for revocation
    }
    
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_token_pair(user_id: str, additional_claims: Optional[dict] = None) -> dict:
    """
    Create both access and refresh tokens.
    
    Returns:
        Dictionary with access_token, refresh_token, token_type, and expires_in
    """
    access_token = create_access_token(user_id, additional_claims=additional_claims)
    refresh_token = create_refresh_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # In seconds
    }


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    
    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[str]:
    """
    Verify an access token and return the user ID.
    
    Returns:
        User ID if token is valid, None otherwise
    """
    payload = decode_token(token)
    if payload is None:
        return None
    
    if payload.get("type") != "access":
        return None
    
    return payload.get("sub")


def verify_refresh_token(token: str) -> Optional[Tuple[str, str]]:
    """
    Verify a refresh token and return user ID and token ID.
    
    Returns:
        Tuple of (user_id, token_id) if valid, None otherwise
    """
    payload = decode_token(token)
    if payload is None:
        return None
    
    if payload.get("type") != "refresh":
        return None
    
    user_id = payload.get("sub")
    token_id = payload.get("jti")
    
    if not user_id or not token_id:
        return None
    
    return user_id, token_id


# =============================================================================
# EMAIL VERIFICATION & PASSWORD RESET TOKENS
# =============================================================================

def create_email_verification_token(email: str, user_id: Optional[str] = None) -> str:
    """Create email verification token."""
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode = {
        "exp": expire,
        "sub": user_id or email,
        "email": email,
        "type": "email_verification",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_email_token(token: str) -> Optional[dict]:
    """Verify email verification token and return payload."""
    payload = decode_token(token)
    if payload is None:
        return None
    
    if payload.get("type") != "email_verification":
        return None
    
    return payload


def create_password_reset_token(user_id: str) -> str:
    """Create password reset token."""
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode = {
        "exp": expire,
        "sub": str(user_id),
        "type": "password_reset",
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return user ID."""
    payload = decode_token(token)
    if payload is None:
        return None
    
    if payload.get("type") != "password_reset":
        return None
    
    return payload.get("sub")


# =============================================================================
# WEBHOOK SIGNATURE
# =============================================================================

def generate_webhook_signature(payload: str, secret: str) -> str:
    """
    Generate HMAC signature for webhook payload.
    
    Args:
        payload: JSON string payload
        secret: Webhook secret
    
    Returns:
        HMAC-SHA256 signature
    """
    import hmac
    signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def verify_webhook_signature(payload: str, secret: str, signature: str) -> bool:
    """
    Verify webhook signature.
    
    Args:
        payload: JSON string payload
        secret: Webhook secret
        signature: Signature to verify
    
    Returns:
        True if signature is valid
    """
    expected = generate_webhook_signature(payload, secret)
    return secrets.compare_digest(expected, signature)
