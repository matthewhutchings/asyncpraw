"""
Reddit OAuth2 authentication endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import asyncpraw
import secrets
from urllib.parse import urlencode
import asyncprawcore

from exceptions import RedditAPIException


router = APIRouter(prefix="/auth", tags=["Authentication"])


class AuthorizationURLRequest(BaseModel):
    """Request to generate OAuth2 authorization URL."""
    client_id: str = Field(..., description="Reddit OAuth2 client ID")
    redirect_uri: str = Field(..., description="OAuth2 redirect URI")
    scopes: List[str] = Field(default=["*"], description="Reddit API scopes")
    state: Optional[str] = Field(None, description="State parameter for security")
    duration: str = Field(default="permanent", description="Token duration (temporary or permanent)")

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "your_reddit_client_id",
                "redirect_uri": "http://localhost:8080/auth/callback",
                "scopes": ["*"],
                "state": "random_state_string",
                "duration": "permanent"
            }
        }


class AuthorizationURLResponse(BaseModel):
    """Response containing OAuth2 authorization URL."""
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
    """OAuth2 callback request with authorization code."""
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
                "redirect_uri": "http://localhost:8080/auth/callback",
                "user_agent": "YourApp/1.0 by your_username"
            }
        }


class RedditTokenResponse(BaseModel):
    """Response containing Reddit access and refresh tokens."""
    access_token: str = Field(..., description="Reddit access token - use as Bearer token")
    refresh_token: Optional[str] = Field(None, description="Reddit refresh token")
    token_type: str = Field(..., description="Token type (usually 'bearer')")
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


@router.post("/authorize-url", response_model=AuthorizationURLResponse)
async def get_authorization_url(request: AuthorizationURLRequest):
    """
    Generate Reddit OAuth2 authorization URL.
    
    Step 1 of OAuth2 flow: Get the URL to redirect users to Reddit for authorization.
    """
    try:
        # Generate state if not provided
        state = request.state or secrets.token_urlsafe(32)
        
        # Build authorization URL
        params = {
            "client_id": request.client_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": request.redirect_uri,
            "duration": request.duration,
            "scope": " ".join(request.scopes)
        }
        
        authorization_url = f"https://www.reddit.com/api/v1/authorize?{urlencode(params)}"
        
        return AuthorizationURLResponse(
            authorization_url=authorization_url,
            state=state
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to generate authorization URL: {str(e)}")


@router.post("/callback", response_model=RedditTokenResponse)
async def oauth2_callback(request: OAuth2CallbackRequest):
    """
    Handle OAuth2 callback and exchange code for tokens.
    
    Step 2 of OAuth2 flow: Exchange authorization code for access and refresh tokens.
    """
    try:
        # Create Reddit instance for token exchange
        reddit = asyncpraw.Reddit(
            client_id=request.client_id,
            client_secret=request.client_secret,
            redirect_uri=request.redirect_uri,
            user_agent=request.user_agent
        )
        
        # Exchange code for tokens
        await reddit.auth.authorize(request.code)
        
        # Get user info to include username
        user = await reddit.user.me()
        username = user.name if user else "unknown"
        
        # Get token info from Reddit instance
        authorizer = reddit._core._authorizer
        
        return RedditTokenResponse(
            access_token=authorizer.access_token,
            refresh_token=authorizer.refresh_token,
            token_type="bearer",
            expires_in=3600,  # Reddit tokens typically expire in 1 hour
            scope="*",  # Reddit doesn't return specific scopes
            reddit_username=username
        )
        
    except Exception as e:
        raise RedditAPIException(f"Failed to exchange code for tokens: {str(e)}")
    finally:
        if 'reddit' in locals():
            await reddit.close()


@router.post("/refresh", response_model=RedditTokenResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    
    Use this endpoint to get a new access token when the current one expires.
    """
    try:
        # Create Reddit instance with refresh token
        reddit = asyncpraw.Reddit(
            client_id=request.client_id,
            client_secret=request.client_secret,
            refresh_token=request.refresh_token,
            user_agent=request.user_agent
        )
        
        # The refresh should happen automatically, get user to trigger it
        user = await reddit.user.me()
        username = user.name if user else "unknown"
        
        # Get updated token info
        authorizer = reddit._core._authorizer
        
        return RedditTokenResponse(
            access_token=authorizer.access_token,
            refresh_token=authorizer.refresh_token or request.refresh_token,
            token_type="bearer",
            expires_in=3600,
            scope="*",
            reddit_username=username
        )
        
    except Exception as e:
        raise RedditAPIException(f"Failed to refresh token: {str(e)}")
    finally:
        if 'reddit' in locals():
            await reddit.close()


@router.get("/validate")
async def validate_token(authorization: str):
    """
    Validate a Reddit access token.
    
    Pass the access token as a Bearer token in the Authorization header.
    """
    try:
        # Extract token from Authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        access_token = authorization[7:]  # Remove "Bearer " prefix
        
        # Create Reddit instance with the token
        reddit = asyncpraw.Reddit(
            token_manager=None,
            user_agent="RedditAPIWrapper/1.0"
        )
        reddit._core._authorizer.access_token = access_token
        
        # Test the token by getting user info
        user = await reddit.user.me()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return {
            "valid": True,
            "username": user.name,
            "message": "Token is valid"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )
    finally:
        if 'reddit' in locals():
            await reddit.close()

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import asyncpraw
from datetime import timedelta
import secrets

from jwt_utils import TokenManager
from exceptions import RedditAPIException


# Security scheme for Swagger UI
security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RedditOAuth2Config(BaseModel):
    """Reddit OAuth2 application configuration."""
    client_id: str = Field(..., description="Reddit OAuth2 client ID")
    client_secret: str = Field(..., description="Reddit OAuth2 client secret")
    redirect_uri: str = Field(..., description="OAuth2 redirect URI")
    user_agent: str = Field(..., description="User agent string")

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "your_reddit_client_id",
                "client_secret": "your_reddit_client_secret",
                "redirect_uri": "http://localhost:8080",
                "user_agent": "YourApp/1.0 by your_username"
            }
        }


class AuthorizationURLRequest(BaseModel):
    """Request to generate OAuth2 authorization URL."""
    client_id: str = Field(..., description="Reddit OAuth2 client ID")
    client_secret: str = Field(..., description="Reddit OAuth2 client secret")
    redirect_uri: str = Field(..., description="OAuth2 redirect URI")
    user_agent: str = Field(..., description="User agent string")
    scopes: List[str] = Field(default=["*"], description="Reddit API scopes")
    state: Optional[str] = Field(None, description="State parameter for security")
    duration: str = Field(default="permanent", description="Token duration (temporary or permanent)")

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "your_reddit_client_id",
                "client_secret": "your_reddit_client_secret",
                "redirect_uri": "http://localhost:8080",
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
    expires_in: int = Field(default=3600, description="URL expiration time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "authorization_url": "https://www.reddit.com/api/v1/authorize?client_id=...",
                "state": "random_state_string",
                "expires_in": 3600
            }
        }


class OAuth2CallbackRequest(BaseModel):
    """OAuth2 callback request with authorization code."""
    client_id: str = Field(..., description="Reddit OAuth2 client ID")
    client_secret: str = Field(..., description="Reddit OAuth2 client secret")
    redirect_uri: str = Field(..., description="OAuth2 redirect URI")
    user_agent: str = Field(..., description="User agent string")
    code: str = Field(..., description="Authorization code from Reddit")
    state: Optional[str] = Field(None, description="State parameter for verification")

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "your_reddit_client_id",
                "client_secret": "your_reddit_client_secret",
                "redirect_uri": "http://localhost:8080",
                "user_agent": "YourApp/1.0 by your_username",
                "code": "authorization_code_from_reddit",
                "state": "random_state_string"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request using a refresh token."""
    client_id: str = Field(..., description="Reddit OAuth2 client ID")
    client_secret: str = Field(..., description="Reddit OAuth2 client secret")
    user_agent: str = Field(..., description="User agent string")
    refresh_token: str = Field(..., description="Reddit refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "your_reddit_client_id",
                "client_secret": "your_reddit_client_secret",
                "user_agent": "YourApp/1.0 by your_username",
                "refresh_token": "your_reddit_refresh_token"
            }
        }


# Legacy support - keeping for backward compatibility
class RedditCredentials(BaseModel):
    """Reddit OAuth2 credentials for authentication (LEGACY - use OAuth2 flow instead)."""
    client_id: str = Field(..., description="Reddit OAuth2 client ID")
    client_secret: str = Field(..., description="Reddit OAuth2 client secret")
    username: str = Field(..., description="Reddit username")
    password: str = Field(..., description="Reddit password")
    user_agent: str = Field(..., description="User agent string")

    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "your_reddit_client_id",
                "client_secret": "your_reddit_client_secret",
                "username": "your_reddit_username",
                "password": "your_reddit_password",
                "user_agent": "YourApp/1.0 by your_username"
            }
        }


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    reddit_username: str = Field(..., description="Authenticated Reddit username")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 43200,
                "reddit_username": "your_username"
            }
        }


class TokenRefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str = Field(..., description="Refresh token")


@router.post("/authorize-url", response_model=AuthorizationURLResponse)
async def get_authorization_url(request: AuthorizationURLRequest):
    """
    Generate Reddit OAuth2 authorization URL.

    This endpoint creates a Reddit OAuth2 authorization URL that users can visit
    to authorize your application. This is the first step in the OAuth2 code flow.

    Steps:
    1. Call this endpoint with your app credentials
    2. Direct user to the returned authorization_url
    3. User authorizes your app on Reddit
    4. Reddit redirects to your redirect_uri with an authorization code
    5. Use the code with /auth/callback to get a JWT token
    """
    try:
        # Create Reddit instance for generating auth URL
        reddit = asyncpraw.Reddit(
            client_id=request.client_id,
            client_secret=request.client_secret,
            redirect_uri=request.redirect_uri,
            user_agent=request.user_agent
        )

        # Generate state if not provided
        state = request.state or secrets.token_urlsafe(32)

        # Generate authorization URL
        auth_url = reddit.auth.url(
            scopes=request.scopes,
            state=state,
            duration=request.duration
        )

        await reddit.close()

        return AuthorizationURLResponse(
            authorization_url=auth_url,
            state=state,
            expires_in=3600  # Authorization URLs typically expire in 1 hour
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate authorization URL: {str(e)}"
        )


@router.post("/callback", response_model=TokenResponse)
async def oauth2_callback(request: OAuth2CallbackRequest):
    """
    Handle OAuth2 callback and exchange authorization code for JWT token.

    After the user authorizes your application on Reddit, they will be redirected
    to your redirect_uri with an authorization code. Use this endpoint to exchange
    that code for a JWT token containing the refresh token.

    The JWT token can then be used for all subsequent API calls.
    """
    try:
        # Create Reddit instance for authorization
        reddit = asyncpraw.Reddit(
            client_id=request.client_id,
            client_secret=request.client_secret,
            redirect_uri=request.redirect_uri,
            user_agent=request.user_agent
        )

        # Exchange code for refresh token
        refresh_token = await reddit.auth.authorize(request.code)

        if not refresh_token:
            await reddit.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain refresh token from authorization code"
            )

        # Get user info to verify the token works
        try:
            user = await reddit.user.me()
            username = user.name
        except Exception as e:
            await reddit.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to verify authorization: {str(e)}"
            )

        await reddit.close()

        # Create JWT token with refresh token (more secure than username/password)
        access_token = TokenManager.create_refresh_token(
            client_id=request.client_id,
            client_secret=request.client_secret,
            user_agent=request.user_agent,
            refresh_token=refresh_token
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=43200,  # 12 hours
            reddit_username=username
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth2 callback failed: {str(e)}"
        )


@router.post("/login-refresh-token", response_model=TokenResponse)
async def login_with_refresh_token(request: RefreshTokenRequest):
    """
    Login using a Reddit refresh token.

    If you already have a Reddit refresh token (from a previous OAuth2 flow
    or from using the Reddit API directly), you can use this endpoint to
    generate a JWT token for API access.

    This is the recommended authentication method for production applications.
    """
    try:
        # Create Reddit instance with refresh token
        reddit = asyncpraw.Reddit(
            client_id=request.client_id,
            client_secret=request.client_secret,
            refresh_token=request.refresh_token,
            user_agent=request.user_agent
        )

        # Test the refresh token by getting user info
        try:
            user = await reddit.user.me()
            username = user.name
        except Exception as e:
            await reddit.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid refresh token: {str(e)}"
            )

        await reddit.close()

        # Create JWT token with refresh token
        access_token = TokenManager.create_refresh_token(
            client_id=request.client_id,
            client_secret=request.client_secret,
            user_agent=request.user_agent,
            refresh_token=request.refresh_token
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=43200,  # 12 hours
            reddit_username=username
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Refresh token authentication failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: RedditCredentials):
    """
    Authenticate with Reddit credentials and receive a JWT token.

    This endpoint accepts Reddit OAuth2 credentials, validates them with Reddit,
    and returns a JWT token that can be used for subsequent API calls.

    The JWT token contains encrypted Reddit credentials and has a configurable
    expiration time (default: 12 hours).
    """
    try:
        # Validate credentials by creating a Reddit client
        reddit = asyncpraw.Reddit(
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            username=credentials.username,
            password=credentials.password,
            user_agent=credentials.user_agent,
            scopes=["*"]
        )

        # Test authentication by accessing user info
        try:
            user = await reddit.user.me()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Reddit credentials"
                )
            authenticated_username = user.name
        except Exception as e:
            await reddit.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Reddit authentication failed: {str(e)}"
            )

        # Close the test connection
        await reddit.close()

        # Create JWT token with Reddit credentials
        access_token = TokenManager.create_reddit_token(
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            username=credentials.username,
            password=credentials.password,
            user_agent=credentials.user_agent
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=43200,  # 12 hours in seconds
            reddit_username=authenticated_username
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/validate", response_model=dict)
async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate a JWT token and return user information.

    This endpoint can be used to check if a token is still valid
    and retrieve information about the authenticated user.
    """
    try:
        # Extract and verify token
        token = credentials.credentials
        reddit_creds = TokenManager.extract_reddit_credentials(token)

        # Create Reddit client to get user info
        reddit = asyncpraw.Reddit(
            client_id=reddit_creds["client_id"],
            client_secret=reddit_creds["client_secret"],
            username=reddit_creds["username"],
            password=reddit_creds["password"],
            user_agent=reddit_creds["user_agent"],
            scopes=["*"]
        )

        try:
            user = await reddit.user.me()
            await reddit.close()

            return {
                "valid": True,
                "username": user.name,
                "user_id": user.id,
                "created_utc": user.created_utc,
                "comment_karma": user.comment_karma,
                "link_karma": user.link_karma
            }
        except Exception as e:
            await reddit.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: TokenRefreshRequest):
    """
    Refresh an expired JWT token.

    Note: This is a placeholder for future implementation.
    Currently, tokens need to be re-issued through the login endpoint.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented. Please login again."
    )


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout and invalidate the current token.

    Note: This is a placeholder for future implementation with token blacklisting.
    Currently, tokens remain valid until expiration.
    """
    return {"message": "Logout successful. Token will expire naturally."}


def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to extract and validate JWT token from Authorization header.

    Returns:
        str: Valid JWT token

    Raises:
        HTTPException: If token is invalid or missing
    """
    try:
        token = credentials.credentials
        # Verify token is valid
        TokenManager.verify_token(token)
        return token
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )