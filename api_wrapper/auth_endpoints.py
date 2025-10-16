from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import asyncpraw
import secrets
from urllib.parse import urlencode

from exceptions import RedditAPIException

router = APIRouter(prefix="/auth", tags=["Authentication"])


class AuthorizationURLRequest(BaseModel):
    """Request to generate OAuth2 authorization URL."""
    client_id: str = Field(..., description="Reddit OAuth2 client ID")
    client_secret: str = Field(..., description="Reddit OAuth2 client secret")
    redirect_uri: str = Field(..., description="OAuth2 redirect URI")
    user_agent: str = Field(..., description="User agent string")
    scopes: list[str] = Field(default=["*"], description="Reddit API scopes")
    state: Optional[str] = Field(None, description="State parameter for security")
    duration: str = Field(default="permanent", description="Token duration")

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "your_reddit_client_id",
                "client_secret": "your_reddit_client_secret",
                "redirect_uri": "http://localhost:8080/callback",
                "user_agent": "YourApp/1.0 by your_username",
                "scopes": ["*"],
                "state": "random_state_string",
                "duration": "permanent"
            }
        }


class AuthorizationURLResponse(BaseModel):
    """OAuth2 authorization URL response."""
    authorization_url: str = Field(..., description="Reddit OAuth2 authorization URL")
    state: str = Field(..., description="State parameter for verification")

    class Config:
        json_schema_extra = {
            "example": {
                "authorization_url": "https://www.reddit.com/api/v1/authorize?client_id=...",
                "state": "random_state_string"
            }
        }


class OAuth2CallbackRequest(BaseModel):
    """OAuth2 callback with authorization code."""
    code: str = Field(..., description="Authorization code from Reddit")
    state: Optional[str] = Field(None, description="State parameter for verification")
    client_id: str = Field(..., description="Reddit OAuth2 client ID")
    client_secret: str = Field(..., description="Reddit OAuth2 client secret")
    redirect_uri: str = Field(..., description="OAuth2 redirect URI")
    user_agent: str = Field(..., description="User agent string")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "authorization_code_from_reddit",
                "state": "random_state_string",
                "client_id": "your_reddit_client_id",
                "client_secret": "your_reddit_client_secret",
                "redirect_uri": "http://localhost:8080/callback",
                "user_agent": "YourApp/1.0 by your_username"
            }
        }


class TokenResponse(BaseModel):
    """Reddit OAuth2 token response."""
    access_token: str = Field(..., description="Reddit access token")
    refresh_token: Optional[str] = Field(None, description="Reddit refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    scope: str = Field(..., description="Granted scopes")
    reddit_username: str = Field(..., description="Authenticated Reddit username")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "reddit_access_token_here",
                "refresh_token": "reddit_refresh_token_here",
                "token_type": "bearer",
                "expires_in": 3600,
                "scope": "*",
                "reddit_username": "your_username"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token using refresh token."""
    refresh_token: str = Field(..., description="Reddit refresh token")
    client_id: str = Field(..., description="Reddit OAuth2 client ID")
    client_secret: str = Field(..., description="Reddit OAuth2 client secret")
    user_agent: str = Field(..., description="User agent string")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "your_reddit_refresh_token",
                "client_id": "your_reddit_client_id",
                "client_secret": "your_reddit_client_secret",
                "user_agent": "YourApp/1.0 by your_username"
            }
        }


class TokenValidationRequest(BaseModel):
    """Request to validate Reddit access token."""
    access_token: str = Field(..., description="Reddit access token to validate")
    client_id: str = Field(..., description="Reddit OAuth2 client ID")
    client_secret: str = Field(..., description="Reddit OAuth2 client secret")
    user_agent: str = Field(..., description="User agent string")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "reddit_access_token_here",
                "client_id": "your_reddit_client_id",
                "client_secret": "your_reddit_client_secret",
                "user_agent": "YourApp/1.0 by your_username"
            }
        }


class TokenValidationResponse(BaseModel):
    """Token validation response."""
    valid: bool = Field(..., description="Whether the token is valid")
    username: Optional[str] = Field(None, description="Reddit username if valid")
    user_id: Optional[str] = Field(None, description="Reddit user ID if valid")
    created_utc: Optional[float] = Field(None, description="Account creation date if valid")
    comment_karma: Optional[int] = Field(None, description="Comment karma if valid")
    link_karma: Optional[int] = Field(None, description="Link karma if valid")
    error: Optional[str] = Field(None, description="Error message if invalid")

    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "username": "example_user",
                "user_id": "abc123",
                "created_utc": 1234567890.0,
                "comment_karma": 1000,
                "link_karma": 500
            }
        }


@router.post("/authorize-url", response_model=AuthorizationURLResponse)
async def get_authorization_url(request: AuthorizationURLRequest):
    """
    Generate Reddit OAuth2 authorization URL.

    Step 1 of OAuth2 flow: Get the URL to redirect users to Reddit for authorization.
    """
    try:
        # Generate state if not provided
        state = request.state or secrets.token_urlsafe(32)

        # Build authorization URL parameters
        params = {
            "client_id": request.client_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": request.redirect_uri,
            "duration": request.duration,
            "scope": " ".join(request.scopes)
        }

        # Create authorization URL
        base_url = "https://www.reddit.com/api/v1/authorize"
        authorization_url = f"{base_url}?{urlencode(params)}"

        return AuthorizationURLResponse(
            authorization_url=authorization_url,
            state=state
        )

    except Exception as e:
        raise RedditAPIException(f"Failed to generate authorization URL: {str(e)}")


@router.post("/callback", response_model=TokenResponse)
async def oauth2_callback(request: OAuth2CallbackRequest):
    """
    Handle OAuth2 callback and exchange code for tokens.

    Step 2 of OAuth2 flow: Exchange authorization code for access and refresh tokens.
    """
    reddit = None
    try:
        # Create Reddit instance for OAuth flow
        reddit = asyncpraw.Reddit(
            client_id=request.client_id,
            client_secret=request.client_secret,
            redirect_uri=request.redirect_uri,
            user_agent=request.user_agent
        )

        # Exchange authorization code for access token
        await reddit.auth.authorize(request.code)

        # Get user info
        user = await reddit.user.me()
        username = user.name if user else "unknown"

        # Get tokens from Reddit's authorizer
        access_token = reddit._core._authorizer.access_token
        refresh_token = getattr(reddit._core._authorizer, 'refresh_token', None)
        scopes = getattr(reddit._core._authorizer, 'scopes', ["*"])

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,  # Reddit tokens typically expire in 1 hour
            scope=" ".join(scopes) if isinstance(scopes, list) else str(scopes),
            reddit_username=username
        )

    except Exception as e:
        raise RedditAPIException(f"Failed to exchange code for tokens: {str(e)}")
    finally:
        if reddit:
            await reddit.close()


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    """
    Refresh an access token using a refresh token.

    Use this when your access token expires to get a new one without re-authorization.
    """
    reddit = None
    try:
        # Create Reddit instance with refresh token
        reddit = asyncpraw.Reddit(
            client_id=request.client_id,
            client_secret=request.client_secret,
            refresh_token=request.refresh_token,
            user_agent=request.user_agent
        )

        # Get user info to verify authentication
        user = await reddit.user.me()
        if not user:
            raise RedditAPIException("Failed to authenticate with refresh token")

        username = user.name

        # Get new tokens
        access_token = reddit._core._authorizer.access_token
        refresh_token = getattr(reddit._core._authorizer, 'refresh_token', request.refresh_token)
        scopes = getattr(reddit._core._authorizer, 'scopes', ["*"])

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            scope=" ".join(scopes) if isinstance(scopes, list) else str(scopes),
            reddit_username=username
        )

    except Exception as e:
        raise RedditAPIException(f"Failed to refresh token: {str(e)}")
    finally:
        if reddit:
            await reddit.close()


@router.post("/validate", response_model=TokenValidationResponse)
async def validate_token(request: TokenValidationRequest):
    """
    Validate a Reddit access token and get user information.

    Check if an access token is still valid and retrieve associated user data.
    """
    reddit = None
    try:
        # Create Reddit instance with access token
        reddit = asyncpraw.Reddit(
            client_id=request.client_id,
            client_secret=request.client_secret,
            user_agent=request.user_agent
        )

        # Set the access token
        reddit._core._authorizer.access_token = request.access_token

        # Try to get user info to validate token
        user = await reddit.user.me()

        return TokenValidationResponse(
            valid=True,
            username=user.name,
            user_id=user.id,
            created_utc=user.created_utc,
            comment_karma=user.comment_karma,
            link_karma=user.link_karma
        )

    except Exception as e:
        return TokenValidationResponse(
            valid=False,
            error=str(e)
        )
    finally:
        if reddit:
            await reddit.close()