"""
User endpoints with header-based authentication support.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
import asyncpraw

from auth import get_reddit_client_with_headers
from exceptions import RedditAPIException

router = APIRouter(tags=["User"])


@router.get("/user/me")
async def get_current_user(
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """
    Get current authenticated user information.

    ## Authentication Options:

    ### Option 1: Access Token Only (Header)
    ```
    Authorization: Bearer <reddit_access_token>
    ```

    ### Option 2: Access Token + Client Credentials (Headers)
    ```
    Authorization: Bearer <reddit_access_token>
    X-Reddit-Client-Id: your_client_id
    X-Reddit-Client-Secret: your_client_secret
    X-Reddit-User-Agent: YourApp/1.0 by your_username
    ```

    The second option provides more authentication context and may be required
    for certain Reddit API operations.
    """
    try:
        user = await reddit.user.me()
        if not user:
            raise HTTPException(status_code=401, detail="Authentication failed")

        return {
            "id": user.id,
            "name": user.name,
            "created_utc": user.created_utc,
            "comment_karma": user.comment_karma,
            "link_karma": user.link_karma,
            "total_karma": user.total_karma if hasattr(user, 'total_karma') else None,
            "is_gold": user.is_gold if hasattr(user, 'is_gold') else False,
            "is_mod": user.is_mod if hasattr(user, 'is_mod') else False,
            "has_verified_email": user.has_verified_email if hasattr(user, 'has_verified_email') else None,
            "inbox_count": user.inbox_count if hasattr(user, 'inbox_count') else None
        }
    except Exception as e:
        raise RedditAPIException(f"Failed to get user info: {str(e)}")


@router.get("/user/{username}")
async def get_user_profile(
    username: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """
    Get public information about a specific user.

    Supports the same authentication options as /user/me.
    """
    try:
        user = await reddit.redditor(username)
        await user.load()

        return {
            "id": user.id,
            "name": user.name,
            "created_utc": user.created_utc,
            "comment_karma": user.comment_karma,
            "link_karma": user.link_karma,
            "total_karma": user.total_karma if hasattr(user, 'total_karma') else None,
            "is_gold": user.is_gold if hasattr(user, 'is_gold') else False,
            "is_mod": user.is_mod if hasattr(user, 'is_mod') else False
        }
    except Exception as e:
        raise RedditAPIException(f"Failed to get user profile: {str(e)}")