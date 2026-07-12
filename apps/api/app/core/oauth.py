"""
OAuth configuration and utilities for Synthesize.io API.
Supports Google OAuth authentication.
"""
from typing import Optional, Dict, Any
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

from app.core.config import settings


# Initialize OAuth
oauth = OAuth()

# Configure Google OAuth only if credentials are provided
if settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_ID != "your-google-oauth-client-id":
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile",
            "prompt": "select_account",
        },
        # Disable CSRF state verification for development (session cookies not reliable in OAuth redirects)
        authorize_state=None if settings.ENVIRONMENT == "development" else None,
    )
    GOOGLE_OAUTH_ENABLED = True
else:
    GOOGLE_OAUTH_ENABLED = False


class GoogleUserInfo:
    """Parsed Google user information."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("sub")
        self.email = data.get("email")
        self.email_verified = data.get("email_verified", False)
        self.name = data.get("name")
        self.given_name = data.get("given_name")
        self.family_name = data.get("family_name")
        self.picture = data.get("picture")
        self.locale = data.get("locale")
        self.raw_data = data
    
    @classmethod
    def from_token(cls, token: Dict[str, Any]) -> "GoogleUserInfo":
        """Create GoogleUserInfo from OAuth token."""
        userinfo = token.get("userinfo", {})
        return cls(userinfo)


def get_google_redirect_uri(request) -> str:
    """Get the Google OAuth redirect URI."""
    # In production, use the configured domain
    if settings.ENVIRONMENT == "production":
        return f"https://api.synthesize.io/api/v1/auth/google/callback"
    
    # In development, use the request's host
    scheme = request.url.scheme
    host = request.url.netloc
    return f"{scheme}://{host}/api/v1/auth/google/callback"


async def get_google_authorization_url(request) -> str:
    """
    Get the Google OAuth authorization URL.
    
    Returns:
        Authorization URL to redirect the user to
    """
    redirect_uri = await get_google_redirect_uri(request)
    # create_authorization_url returns a tuple: (url, state)
    authorization_data = await oauth.google.create_authorization_url(redirect_uri)
    # Return just the URL if it's a tuple, otherwise return the data as-is
    if isinstance(authorization_data, tuple):
        return authorization_data[0]
    elif isinstance(authorization_data, dict):
        return authorization_data.get('url', authorization_data)
    return authorization_data


async def authorize_google(request) -> Dict[str, Any]:
    """
    Exchange authorization code for tokens and user info.
    
    Returns:
        OAuth token containing user information
    """
    redirect_uri = await get_google_redirect_uri(request)
    token = await oauth.google.authorize_access_token(request)
    return token


def parse_google_userinfo(token: Dict[str, Any]) -> GoogleUserInfo:
    """
    Parse user information from Google OAuth token.
    
    Args:
        token: OAuth token from Google
    
    Returns:
        GoogleUserInfo object
    """
    return GoogleUserInfo.from_token(token)


# =============================================================================
# GITHUB OAUTH (Future implementation)
# =============================================================================

if settings.GITHUB_CLIENT_ID:
    oauth.register(
        name="github",
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )


class GitHubUserInfo:
    """Parsed GitHub user information."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = str(data.get("id"))
        self.login = data.get("login")
        self.email = data.get("email")
        self.name = data.get("name")
        self.avatar_url = data.get("avatar_url")
        self.raw_data = data
