"""
Authentication service for Synthesize.io API.

Handles user registration, login, token management, and OAuth flows.
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    TokenExpiredError,
    InvalidTokenError,
    DuplicateError,
    NotFoundError,
    ValidationError,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_token_pair,
    verify_access_token,
    verify_refresh_token,
    create_email_verification_token,
    verify_email_token,
    create_password_reset_token,
    verify_password_reset_token,
)
from app.models import User, Session, OAuthAccount
from app.services.email_service import email_service
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    AuthUserResponse,
    LoginResponse,
    RegisterResponse,
)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # REGISTRATION
    # =========================================================================
    
    def register(
        self,
        data: RegisterRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> RegisterResponse:
        """Register a new user."""
        # Check if email already exists
        existing = self._get_user_by_email(data.email)
        if existing:
            raise DuplicateError("User", "email", data.email)
        
        # Create user
        user = User(
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            role="user",
            status="active",
            email_verified=False,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Send verification email
        verification_token = create_email_verification_token(user.email, str(user.id))
        email_service.send_verification_email(user.email, verification_token)
        
        # Create tokens
        tokens = create_token_pair(
            user_id=str(user.id),
            additional_claims={"email": user.email, "role": user.role}
        )
        
        # Store refresh token
        self._store_refresh_token(
            user_id=user.id,
            token=tokens["refresh_token"],
            user_agent=user_agent,
        )
        
        # Record login
        user.last_login_at = datetime.utcnow()
        self.db.commit()
        
        # Build response
        token_response = TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        
        user_response = AuthUserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            email_verified=user.email_verified,
            role=user.role,
            status=user.status,
        )
        
        return RegisterResponse(
            message="Registration successful. Please verify your email.",
            user=user_response,
            token=token_response,
        )
    
    # =========================================================================
    # LOGIN
    # =========================================================================
    
    def login(
        self,
        data: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> LoginResponse:
        """Authenticate user and return tokens."""
        # Get user
        user = self._get_user_by_email(data.email)
        if not user:
            raise InvalidCredentialsError()
        
        # Check password
        if not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError()
        
        # Check user status
        if user.status == "inactive":
            raise AuthenticationError("Your account is inactive")
        if user.status == "suspended":
            raise AuthenticationError("Your account has been suspended")
        if user.status == "deleted":
            raise InvalidCredentialsError()
        
        # Create tokens
        token_expiry = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        if data.remember_me:
            token_expiry = 60 * 24 * 30  # 30 days
        
        tokens = create_token_pair(
            user_id=str(user.id),
            additional_claims={"email": user.email, "role": user.role}
        )
        
        # Store refresh token
        self._store_refresh_token(
            user_id=user.id,
            token=tokens["refresh_token"],
            user_agent=user_agent,
            remember_me=data.remember_me,
        )
        
        # Update login stats
        user.last_login_at = datetime.utcnow()
        user.failed_login_attempts = 0
        self.db.commit()
        
        # Build response
        token_response = TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=token_expiry * 60,
        )
        
        user_response = AuthUserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            email_verified=user.email_verified,
            role=user.role,
            status=user.status,
        )
        
        return LoginResponse(token=token_response, user=user_response)
    
    # =========================================================================
    # TOKEN MANAGEMENT
    # =========================================================================
    
    def refresh_tokens(
        self,
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Refresh access token using refresh token."""
        # Verify the token
        result = verify_refresh_token(refresh_token)
        if not result:
            raise InvalidTokenError()
        
        user_id, token_id = result
        
        # Check if refresh token exists in database
        stored_token = self._get_refresh_token(refresh_token)
        if not stored_token:
            raise InvalidTokenError()
        
        if stored_token.revoked_at:
            raise InvalidTokenError("Token has been revoked")
        
        if stored_token.expires_at < datetime.utcnow():
            raise TokenExpiredError()
        
        # Get user
        user = self._get_user_by_id(UUID(user_id))
        if not user or user.status != "active":
            raise AuthenticationError("User not found or inactive")
        
        # Create new tokens
        tokens = create_token_pair(
            user_id=str(user.id),
            additional_claims={"email": user.email, "role": user.role}
        )
        
        # Revoke old refresh token
        stored_token.revoked_at = datetime.utcnow()
        
        # Store new refresh token
        self._store_refresh_token(
            user_id=user.id,
            token=tokens["refresh_token"],
            user_agent=user_agent,
        )
        
        self.db.commit()
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    def logout(self, refresh_token: str) -> None:
        """Logout user by revoking refresh token."""
        stored_token = self._get_refresh_token(refresh_token)
        if stored_token:
            stored_token.revoked_at = datetime.utcnow()
            self.db.commit()
    
    def logout_all(self, user_id: UUID) -> int:
        """Logout from all devices by revoking all refresh tokens."""
        result = self.db.execute(
            select(Session)
            .where(Session.user_id == user_id)
            .where(Session.revoked_at.is_(None))
        )
        sessions = result.scalars().all()
        
        count = 0
        for session in sessions:
            session.revoked_at = datetime.utcnow()
            count += 1
        
        self.db.commit()
        return count
    
    # =========================================================================
    # EMAIL VERIFICATION
    # =========================================================================
    
    def send_verification_email(self, user_id: UUID) -> str:
        """Generate verification token and send email."""
        user = self._get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        
        if user.email_verified:
            raise ValidationError("Email is already verified")
        
        token = create_email_verification_token(user.email, str(user.id))
        
        # Send email via email service
        email_service.send_verification_email(user.email, token)
        
        return token
    
    def verify_email(self, token: str) -> User:
        """Verify user's email with token."""
        payload = verify_email_token(token)
        if not payload:
            raise InvalidTokenError("Invalid or expired verification token")
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        user = self._get_user_by_id(UUID(user_id))
        if not user:
            raise NotFoundError("User", user_id)
        
        if user.email.lower() != email.lower():
            raise InvalidTokenError("Token does not match user email")
        
        user.email_verified = True
        user.email_verified_at = datetime.utcnow()
        self.db.commit()
        
        # Send welcome email
        email_service.send_welcome_email(user.email, user.first_name)
        
        return user
    
    # =========================================================================
    # PASSWORD RESET
    # =========================================================================
    
    def send_password_reset(self, email: str) -> Optional[str]:
        """Generate password reset token and send email."""
        user = self._get_user_by_email(email)
        if not user:
            # Don't reveal if user exists
            return None
        
        token = create_password_reset_token(str(user.id))
        
        # Send email via email service
        email_service.send_password_reset_email(user.email, token)
        
        return token
    
    def reset_password(self, token: str, new_password: str) -> User:
        """Reset user's password with token."""
        payload = verify_password_reset_token(token)
        if not payload:
            raise InvalidTokenError("Invalid or expired reset token")
        
        user_id = payload.get("sub")
        
        user = self._get_user_by_id(UUID(user_id))
        if not user:
            raise NotFoundError("User", user_id)
        
        user.password_hash = hash_password(new_password)
        user.password_changed_at = datetime.utcnow()
        
        # Revoke all refresh tokens for security
        self.logout_all(user.id)
        
        self.db.commit()
        
        return user
    
    # =========================================================================
    # OAUTH
    # =========================================================================
    
    def oauth_login(
        self,
        provider: str,
        provider_user_id: str,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> LoginResponse:
        """Handle OAuth login/registration."""
        # Check if user exists by email
        user = self._get_user_by_email(email)
        
        if not user:
            # Create new user
            user = User(
                email=email.lower(),
                first_name=first_name,
                last_name=last_name,
                avatar_url=avatar_url,
                role="user",
                status="active",
                email_verified=True,  # OAuth emails are pre-verified
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            # Create OAuth account link
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_user_id=provider_user_id,
                provider_email=email,
            )
            self.db.add(oauth_account)
            self.db.commit()
        else:
            # If user is deleted, reactivate their account
            if user.status == "deleted":
                user.status = "active"
                user.email_verified = True
                user.deleted_at = None
                # Update profile info from OAuth
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                if avatar_url:
                    user.avatar_url = avatar_url
                self.db.commit()
            
            # Check if OAuth account already linked
            result = self.db.execute(
                select(OAuthAccount).where(
                    OAuthAccount.user_id == user.id,
                    OAuthAccount.provider == provider
                )
            )
            oauth_account = result.scalar_one_or_none()
            
            if not oauth_account:
                # Link OAuth account to existing user
                oauth_account = OAuthAccount(
                    user_id=user.id,
                    provider=provider,
                    provider_user_id=provider_user_id,
                    provider_email=email,
                )
                self.db.add(oauth_account)
                self.db.commit()
            
            # Update avatar if user doesn't have one
            if not user.avatar_url and avatar_url:
                user.avatar_url = avatar_url
                self.db.commit()
        
        # Check user status (after potential reactivation)
        if user.status == "suspended":
            raise AuthenticationError("Your account has been suspended")
        
        # Create tokens
        tokens = create_token_pair(
            user_id=str(user.id),
            additional_claims={"email": user.email, "role": user.role}
        )
        
        # Store refresh token
        self._store_refresh_token(
            user_id=user.id,
            token=tokens["refresh_token"],
            user_agent=user_agent,
        )
        
        # Update login stats
        user.last_login_at = datetime.utcnow()
        self.db.commit()
        
        # Build response
        token_response = TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        
        user_response = AuthUserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            email_verified=user.email_verified,
            role=user.role,
            status=user.status,
        )
        
        return LoginResponse(token=token_response, user=user_response)
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = self.db.execute(
            select(User).where(func.lower(User.email) == email.lower())
        )
        return result.scalar_one_or_none()
    
    def _get_refresh_token(self, token: str) -> Optional[Session]:
        """Get refresh token from database."""
        result = self.db.execute(
            select(Session).where(Session.refresh_token_hash == token)
        )
        return result.scalar_one_or_none()
    
    def _store_refresh_token(
        self,
        user_id: UUID,
        token: str,
        user_agent: Optional[str] = None,
        remember_me: bool = False,
    ) -> Session:
        """Store refresh token in database."""
        expires_days = 30 if remember_me else 7
        
        session = Session(
            user_id=user_id,
            token_hash=token,  # Store access token hash
            refresh_token_hash=token,  # Store refresh token hash
            expires_at=datetime.utcnow() + timedelta(days=expires_days),
            refresh_expires_at=datetime.utcnow() + timedelta(days=expires_days),
            device_info={"user_agent": user_agent} if user_agent else None,
        )
        
        self.db.add(session)
        self.db.flush()
        
        return session


# Dependency injection helper
def get_auth_service(db: Session) -> AuthService:
    """Get auth service instance."""
    return AuthService(db)
