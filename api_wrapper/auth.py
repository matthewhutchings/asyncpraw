"""
Reddit token-based authentication module for Reddit API access.
"""

from typing import Optional, Dict
import asyncpraw
from fastapi import HTTPException, Depends, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security scheme
security = HTTPBearer()

# Cache for Reddit clients to avoid recreating them
_reddit_client_cache: Dict[str, asyncpraw.Reddit] = {}


async def get_reddit_client_with_headers(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    x_reddit_client_id: Optional[str] = Header(None, alias="X-Reddit-Client-Id"),
    x_reddit_client_secret: Optional[str] = Header(None, alias="X-Reddit-Client-Secret"),
    x_reddit_user_agent: Optional[str] = Header(None, alias="X-Reddit-User-Agent")
) -> asyncpraw.Reddit:
    """
    Create and return an authenticated Reddit client using Reddit's access token and optional client credentials from headers.

    This function takes a Reddit access token and optionally client credentials from headers
    to create an AsyncPRAW Reddit instance.

    Args:
        credentials: HTTP Bearer token credentials (Reddit access token)
        x_reddit_client_id: Reddit app client ID from header
        x_reddit_client_secret: Reddit app client secret from header
        x_reddit_user_agent: User agent string from header

    Returns:
        asyncpraw.Reddit: Authenticated Reddit client

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Extract Reddit access token
        access_token = credentials.credentials

        # Debug: Log the received headers
        print(f"DEBUG: Received access_token: {access_token[:20] if access_token else 'None'}...")
        print(f"DEBUG: Received client_id: {x_reddit_client_id}")
        print(f"DEBUG: Received client_secret: {'***' if x_reddit_client_secret else 'None'}")
        print(f"DEBUG: Received user_agent: {x_reddit_user_agent}")

        # Use default user agent if not provided
        user_agent = x_reddit_user_agent or "RedditAPIWrapper/1.0"

        # Create cache key (include client_id if provided for uniqueness)
        cache_key_parts = [access_token[:16]]
        if x_reddit_client_id:
            cache_key_parts.append(x_reddit_client_id[:8])
        cache_key = f"reddit_{'_'.join(cache_key_parts)}"

        # Check if we have a cached client
        if cache_key in _reddit_client_cache:
            reddit = _reddit_client_cache[cache_key]

            # Test if the cached client is still valid
            try:
                user = await reddit.user.me()
                if user is not None:
                    return reddit
                else:
                    # Remove invalid client from cache
                    del _reddit_client_cache[cache_key]
            except Exception:
                # Remove invalid client from cache
                if cache_key in _reddit_client_cache:
                    del _reddit_client_cache[cache_key]

        # Create new Reddit client
        if x_reddit_client_id and x_reddit_client_secret:
            # Create client with provided credentials
            print(f"DEBUG: Creating Reddit client with credentials")
            reddit = asyncpraw.Reddit(
                client_id=x_reddit_client_id,
                client_secret=x_reddit_client_secret,
                user_agent=user_agent
            )
        else:
            # Create client without credentials (token-only mode)
            print(f"DEBUG: Creating Reddit client without credentials (token-only)")
            reddit = asyncpraw.Reddit(
                token_manager=None,
                user_agent=user_agent
            )

        # Set the access token directly
        reddit._core._authorizer.access_token = access_token
        print(f"DEBUG: Set access token on Reddit client")

        # Test authentication
        try:
            print(f"DEBUG: Testing authentication with reddit.user.me()")
            user = await reddit.user.me()
            if user is None:
                await reddit.close()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to authenticate with Reddit API - invalid token"
                )
            print(f"DEBUG: Authentication successful for user: {user.name}")
        except Exception as e:
            print(f"DEBUG: Authentication test failed: {str(e)}")
            await reddit.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Reddit authentication failed: {str(e)}"
            )

        # Cache the client
        _reddit_client_cache[cache_key] = reddit

        return reddit

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


async def get_reddit_client(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> asyncpraw.Reddit:
    """
    Create and return an authenticated Reddit client using Reddit's access token.

    This function takes a Reddit access token directly and creates
    an AsyncPRAW Reddit instance using Reddit's native authentication.

    Args:
        credentials: HTTP Bearer token credentials (Reddit access token)

    Returns:
        asyncpraw.Reddit: Authenticated Reddit client

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Extract Reddit access token
        access_token = credentials.credentials

        # Create cache key from token (first 16 chars for security)
        cache_key = f"reddit_token_{access_token[:16]}"

        # Check if we have a cached client
        if cache_key in _reddit_client_cache:
            reddit = _reddit_client_cache[cache_key]

            # Test if the cached client is still valid
            try:
                user = await reddit.user.me()
                if user is not None:
                    return reddit
                else:
                    # Remove invalid client from cache
                    del _reddit_client_cache[cache_key]
            except Exception:
                # Remove invalid client from cache
                if cache_key in _reddit_client_cache:
                    del _reddit_client_cache[cache_key]

        # Create new Reddit client using the access token directly
        reddit = asyncpraw.Reddit(
            token_manager=None,  # We'll set the token manually
            user_agent="RedditAPIWrapper/1.0"
        )

        # Set the access token directly
        reddit._core._authorizer.access_token = access_token

        # Test authentication
        try:
            user = await reddit.user.me()
            if user is None:
                await reddit.close()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to authenticate with Reddit API - invalid token"
                )
        except Exception as e:
            await reddit.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Reddit authentication failed: {str(e)}"
            )

        # Cache the client
        _reddit_client_cache[cache_key] = reddit

        return reddit

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


async def get_current_user_reddit_client(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> asyncpraw.Reddit:
    """
    Alternative name for get_reddit_client for clarity.
    """
    return await get_reddit_client(credentials)


def clear_reddit_client_cache():
    """
    Clear the Reddit client cache.
    Useful for testing or when credentials change.
    """
    global _reddit_client_cache
    _reddit_client_cache.clear()


def get_cached_client_count() -> int:
    """
    Get the number of cached Reddit clients.
    Useful for monitoring and debugging.
    """
    return len(_reddit_client_cache)