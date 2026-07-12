"""
Authentication endpoints for Synthesize.io API.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.api.deps import DBSession, CurrentUser
from app.core.config import settings
from app.core.oauth import oauth, get_google_authorization_url, get_google_redirect_uri, GOOGLE_OAUTH_ENABLED
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    VerifyEmailRequest,
    TokenResponse,
    LoginResponse,
    RegisterResponse,
    SessionListResponse,
)
from app.schemas.base import MessageResponse


router = APIRouter()


# =============================================================================
# REGISTRATION & LOGIN
# =============================================================================

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(
    request: Request,
    data: RegisterRequest,
    db: DBSession,
):
    """Register a new user account."""
    auth_service = AuthService(db)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    return auth_service.register(
        data=data,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login with email and password",
)
def login(
    request: Request,
    data: LoginRequest,
    db: DBSession,
):
    """Authenticate user and return JWT tokens."""
    auth_service = AuthService(db)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    return auth_service.login(
        data=data,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout user",
)
def logout(
    data: RefreshTokenRequest,
    db: DBSession,
    user: CurrentUser,
):
    """Logout user by invalidating refresh token."""
    auth_service = AuthService(db)
    auth_service.logout(data.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.post(
    "/logout-all",
    response_model=MessageResponse,
    summary="Logout from all devices",
)
def logout_all(
    db: DBSession,
    user: CurrentUser,
):
    """Logout from all devices by invalidating all refresh tokens."""
    auth_service = AuthService(db)
    count = auth_service.logout_all(user.id)
    return MessageResponse(message=f"Logged out from {count} sessions")


# =============================================================================
# TOKEN MANAGEMENT
# =============================================================================

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
def refresh_token(
    request: Request,
    data: RefreshTokenRequest,
    db: DBSession,
):
    """Get new access token using refresh token."""
    auth_service = AuthService(db)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    return auth_service.refresh_tokens(
        refresh_token=data.refresh_token,
        ip_address=ip_address,
        user_agent=user_agent,
    )


# =============================================================================
# EMAIL VERIFICATION
# =============================================================================

@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email address",
)
def verify_email(
    data: VerifyEmailRequest,
    db: DBSession,
):
    """Verify user's email address using verification token."""
    auth_service = AuthService(db)
    auth_service.verify_email(data.token)
    return MessageResponse(message="Email verified successfully")


@router.post(
    "/resend-verification",
    response_model=MessageResponse,
    summary="Resend verification email",
)
def resend_verification(
    db: DBSession,
    user: CurrentUser,
):
    """Resend email verification link."""
    auth_service = AuthService(db)
    auth_service.send_verification_email(user.id)
    return MessageResponse(message="Verification email sent")


# =============================================================================
# PASSWORD RESET
# =============================================================================

@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset",
)
def forgot_password(
    data: ForgotPasswordRequest,
    db: DBSession,
):
    """Request password reset email."""
    auth_service = AuthService(db)
    auth_service.send_password_reset(data.email)
    return MessageResponse(
        message="If an account exists with this email, a password reset link has been sent"
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password",
)
def reset_password(
    data: ResetPasswordRequest,
    db: DBSession,
):
    """Reset password using reset token."""
    auth_service = AuthService(db)
    auth_service.reset_password(data.token, data.password)
    return MessageResponse(message="Password reset successfully")


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
)
def change_password(
    data: ChangePasswordRequest,
    db: DBSession,
    user: CurrentUser,
):
    """Change password for authenticated user."""
    from app.services.user_service import UserService
    user_service = UserService(db)
    user_service.change_password(
        user_id=user.id,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    return MessageResponse(message="Password changed successfully")


# =============================================================================
# OAUTH - GOOGLE
# =============================================================================

@router.get("/google", summary="Initiate Google OAuth")
def google_auth_redirect(request: Request):
    """Redirect to Google OAuth authorization page."""
    if not GOOGLE_OAUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured. Please set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in your .env.local file. See https://console.cloud.google.com/apis/credentials for setup instructions."
        )
    
    # Build OAuth URL manually without state for development
    redirect_uri = get_google_redirect_uri(request)
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_OAUTH_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&prompt=select_account"
    )
    return RedirectResponse(url=auth_url)


@router.get("/google/callback", summary="Google OAuth callback")
def google_auth_callback(
    request: Request,
    db: DBSession,
    code: str,
    state: Optional[str] = None,
):
    """Handle Google OAuth callback and authenticate user."""
    if not GOOGLE_OAUTH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured."
        )
    try:
        # Get the redirect URI
        redirect_uri = get_google_redirect_uri(request)
        
        # Exchange code for tokens manually (bypass authlib state validation)
        import httpx
        with httpx.Client() as client:
            token_response = client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange code for token: {token_response.text}",
                )
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            # Get user info from Google
            userinfo_response = client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        
        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google",
            )
        
        user_info = userinfo_response.json()
        
        auth_service = AuthService(db)
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        result = auth_service.oauth_login(
            provider="google",
            provider_user_id=user_info.get("id"),
            email=user_info.get("email"),
            first_name=user_info.get("given_name"),
            last_name=user_info.get("family_name"),
            avatar_url=user_info.get("picture"),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        frontend_url = settings.FRONTEND_URL
        redirect_url = (
            f"{frontend_url}/auth/callback"
            f"?access_token={result.token.access_token}"
            f"&refresh_token={result.token.refresh_token}"
        )
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        frontend_url = settings.FRONTEND_URL
        error_msg = str(e).replace(" ", "%20")
        redirect_url = f"{frontend_url}/auth/callback?error={error_msg}"
        return RedirectResponse(url=redirect_url)


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

@router.get("/sessions", response_model=SessionListResponse, summary="Get active sessions")
def get_sessions(db: DBSession, user: CurrentUser):
    """Get list of active sessions for current user."""
    from app.services.user_service import UserService
    user_service = UserService(db)
    sessions = user_service.get_sessions(user.id)
    
    return SessionListResponse(
        sessions=[
            {
                "id": s.id,
                "device_info": s.device_info,
                "ip_address": s.ip_address,
                "created_at": s.created_at,
                "expires_at": s.expires_at,
                "is_current": False,
            }
            for s in sessions
        ],
        total=len(sessions),
    )


@router.delete("/sessions/{session_id}", response_model=MessageResponse, summary="Revoke a session")
def revoke_session(session_id: str, db: DBSession, user: CurrentUser):
    """Revoke a specific session."""
    from uuid import UUID
    from app.services.user_service import UserService
    user_service = UserService(db)
    user_service.revoke_session(user.id, UUID(session_id))
    return MessageResponse(message="Session revoked")


# =============================================================================
# CURRENT USER
# =============================================================================

@router.get("/me", summary="Get current user")
def get_current_user_info(user: CurrentUser):
    """Get current authenticated user's information."""
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "email_verified": user.email_verified,
        "role": user.role,
        "status": user.status,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
