"""
Reddit API Wrapper - FastAPI Application

A comprehensive REST API wrapper around Async PRAW for Reddit API access.
Provides OAuth2 authentication and full Reddit functionality through HTTP endpoints.
"""

from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
import asyncio
import logging

from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncpraw
from asyncpraw.exceptions import AsyncPRAWException

from models import (
    SubredditInfo, SubmissionInfo, SubmissionCreate, CommentInfo,
    CommentCreate, UserInfo, ErrorResponse, HealthResponse,
    MessageInfo, MessageCreate, DraftInfo, DraftCreate, DraftUpdate,
    PollSubmissionCreate, GallerySubmissionCreate, LiveThreadInfo, LiveThreadCreate
)
from auth import get_reddit_client
from exceptions import RedditAPIException
import additional_endpoints
import auth_endpoints


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Reddit API Wrapper")
    yield
    logger.info("Shutting down Reddit API Wrapper")


# Initialize FastAPI app
app = FastAPI(
    title="Reddit API Wrapper",
    description="""
    A comprehensive REST API wrapper around Async PRAW for Reddit API access.

    This API provides JWT-based authentication using Reddit's OAuth2 code flow for
    secure and scalable Reddit API access.

    ## Features

    ### Core Reddit Functionality
    - **Subreddits**: Browse, search, subscribe/unsubscribe, get moderators
    - **Submissions**: Create, edit, delete, vote, save/unsave, crosspost
    - **Comments**: Create, edit, delete, vote, save/unsave, reply
    - **Users**: Get profiles, submissions, comments, karma breakdown

    ### Advanced Submission Types
    - **Polls**: Create poll submissions with multiple options
    - **Images**: Upload and submit images
    - **Galleries**: Create multi-image gallery posts
    - **Videos**: Upload and submit videos with thumbnails

    ### Inbox & Messaging
    - **Inbox**: Get all messages, unread, mentions, comment/submission replies
    - **Messages**: Send private messages, delete, mark read/unread
    - **User Management**: Block/unblock users, manage friends

    ### Draft Management
    - **Drafts**: Create, list, update, delete, and submit drafts
    - **Full CRUD**: Complete draft lifecycle management

    ### Live Threads
    - **Live Updates**: Create and manage live threads
    - **Contributors**: Manage live thread contributors
    - **Real-time**: Add updates to ongoing live events

    ### Content Management
    - **Editing**: Edit submissions and comments
    - **Moderation**: Report content, approve/remove posts
    - **Saved Content**: Save/unsave and retrieve saved items

    ### User Preferences & Settings
    - **Preferences**: Get and update user preferences
    - **Subscriptions**: Manage subreddit subscriptions
    - **Multireddits**: Access user's multireddits
    - **Inbox Toggles**: Enable/disable inbox replies

    ### Data Refresh & Context
    - **Refresh**: Update comment and submission data
    - **Context**: Get comment context and parent relationships
    - **Comment Trees**: Load and manage comment forests

    ## 🔐 Authentication Methods

    ### Method 1: OAuth2 Code Flow (Recommended)

    The secure way to authenticate without storing usernames/passwords:

    1. **Get Authorization URL**: POST `/auth/authorize-url` → Get Reddit authorization URL
    2. **User Authorization**: Direct user to the URL to authorize your app
    3. **Handle Callback**: POST `/auth/callback` with authorization code → Get JWT token
    4. **Use Token**: Include JWT token in Authorization header for API calls

    ### Method 2: Refresh Token (For Existing Tokens)

    If you already have a Reddit refresh token:

    1. **Login with Refresh Token**: POST `/auth/login-refresh-token` → Get JWT token
    2. **Use Token**: Include JWT token in Authorization header for API calls

    ### Method 3: Username/Password (Legacy, Not Recommended)

    For backward compatibility only - use OAuth2 flow in production:

    1. **Legacy Login**: POST `/auth/login` with username/password → Get JWT token
    2. **Use Token**: Include JWT token in Authorization header for API calls

    ## 🚀 Quick Start - OAuth2 Flow

    ### 1. Reddit App Setup
    Create a Reddit app at: https://www.reddit.com/prefs/apps/
    - Choose "web app" type
    - Set redirect URI (e.g., `http://localhost:8080`)
    - Note your client_id and client_secret

    ### 2. Get Authorization URL
    ```bash
    curl -X POST "http://localhost:8000/auth/authorize-url" \\
      -H "Content-Type: application/json" \\
      -d '{
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "redirect_uri": "http://localhost:8080",
        "user_agent": "YourApp/1.0 by your_username"
      }'
    ```

    ### 3. User Authorization
    Direct the user to visit the returned `authorization_url`

    ### 4. Handle Callback
    After user authorization, exchange the code for a JWT token:
    ```bash
    curl -X POST "http://localhost:8000/auth/callback" \\
      -H "Content-Type: application/json" \\
      -d '{
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "redirect_uri": "http://localhost:8080",
        "user_agent": "YourApp/1.0 by your_username",
        "code": "authorization_code_from_reddit"
      }'
    ```

    ### 5. Use the API
    ```bash
    curl "http://localhost:8000/subreddit/python/hot" \\
      -H "Authorization: Bearer <your_jwt_token>"
    ```

    ## ✨ Features

    - **Secure OAuth2 Flow**: No username/password storage required
    - **JWT Token Authentication**: Stateless, scalable authentication
    - **Refresh Token Support**: Long-lived authentication
    - **Client Caching**: Optimized Reddit connection management
    - **Complete Reddit API**: All core Reddit functionality
    - **Auto Documentation**: Interactive Swagger UI
    - **Production Ready**: Docker support, monitoring, security features

    ## 🔒 Security Benefits

    - ✅ **No Password Storage**: OAuth2 flow eliminates password requirements
    - ✅ **Encrypted Tokens**: JWT tokens contain encrypted Reddit credentials
    - ✅ **Token Expiration**: Configurable token lifetime (default: 12 hours)
    - ✅ **Revokable Access**: Users can revoke access from Reddit settings
    - ✅ **Audit Trail**: Reddit provides OAuth2 access logs
    """,
    version="1.0.0",
    contact={
        "name": "Reddit API Wrapper",
        "url": "https://github.com/praw-dev/asyncpraw",
    },
    license_info={
        "name": "BSD License",
        "url": "https://github.com/praw-dev/asyncpraw/blob/main/LICENSE.txt",
    },
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include additional endpoints
app.include_router(additional_endpoints.router)
app.include_router(auth_endpoints.router)

# Include new functionality routers
try:
    import inbox_endpoints
    app.include_router(inbox_endpoints.router)
except ImportError:
    logger.warning("inbox_endpoints module not found")

try:
    import content_endpoints
    app.include_router(content_endpoints.router)
except ImportError:
    logger.warning("content_endpoints module not found")

try:
    import draft_endpoints
    app.include_router(draft_endpoints.router)
except ImportError:
    logger.warning("draft_endpoints module not found")

try:
    import advanced_submissions
    app.include_router(advanced_submissions.router)
except ImportError:
    logger.warning("advanced_submissions module not found")

try:
    import settings_endpoints
    app.include_router(settings_endpoints.router)
except ImportError:
    logger.warning("settings_endpoints module not found")

try:
    import live_endpoints
    app.include_router(live_endpoints.router)
except ImportError:
    logger.warning("live_endpoints module not found")

try:
    import refresh_endpoints
    app.include_router(refresh_endpoints.router)
except ImportError:
    logger.warning("refresh_endpoints module not found")

try:
    import subreddit_management
    app.include_router(subreddit_management.router)
except ImportError:
    logger.warning("subreddit_management module not found")

try:
    import user_endpoints
    app.include_router(user_endpoints.router)
except ImportError:
    logger.warning("user_endpoints module not found")


@app.exception_handler(RedditAPIException)
async def reddit_api_exception_handler(request, exc: RedditAPIException):
    """Handle Reddit API exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "detail": exc.detail}
    )


@app.exception_handler(AsyncPRAWException)
async def asyncpraw_exception_handler(request, exc: AsyncPRAWException):
    """Handle AsyncPRAW exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Reddit API Error", "detail": str(exc)}
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Reddit API Wrapper"}


# Subreddit endpoints
@app.get("/subreddit/{subreddit_name}", response_model=SubredditInfo, tags=["Subreddits"])
async def get_subreddit_info(
    subreddit_name: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get information about a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        await subreddit.load()

        return SubredditInfo(
            name=subreddit.display_name,
            title=subreddit.title,
            description=subreddit.description,
            subscribers=subreddit.subscribers,
            created_utc=subreddit.created_utc,
            over18=subreddit.over18,
            public_description=subreddit.public_description
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to get subreddit info: {str(e)}")


@app.get("/subreddit/{subreddit_name}/hot", response_model=List[SubmissionInfo], tags=["Subreddits"])
async def get_subreddit_hot(
    subreddit_name: str,
    limit: int = 25,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get hot submissions from a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        submissions = []

        async for submission in subreddit.hot(limit=limit):
            submissions.append(SubmissionInfo(
                id=submission.id,
                title=submission.title,
                author=submission.author.name if submission.author else "[deleted]",
                score=submission.score,
                url=submission.url,
                permalink=f"https://reddit.com{submission.permalink}",
                created_utc=submission.created_utc,
                num_comments=submission.num_comments,
                selftext=submission.selftext,
                is_self=submission.is_self,
                over_18=submission.over_18,
                subreddit=submission.subreddit.display_name
            ))

        return submissions
    except Exception as e:
        raise RedditAPIException(f"Failed to get hot submissions: {str(e)}")


@app.get("/subreddit/{subreddit_name}/new", response_model=List[SubmissionInfo], tags=["Subreddits"])
async def get_subreddit_new(
    subreddit_name: str,
    limit: int = 25,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get new submissions from a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        submissions = []

        async for submission in subreddit.new(limit=limit):
            submissions.append(SubmissionInfo(
                id=submission.id,
                title=submission.title,
                author=submission.author.name if submission.author else "[deleted]",
                score=submission.score,
                url=submission.url,
                permalink=f"https://reddit.com{submission.permalink}",
                created_utc=submission.created_utc,
                num_comments=submission.num_comments,
                selftext=submission.selftext,
                is_self=submission.is_self,
                over_18=submission.over_18,
                subreddit=submission.subreddit.display_name
            ))

        return submissions
    except Exception as e:
        raise RedditAPIException(f"Failed to get new submissions: {str(e)}")


@app.post("/subreddit/{subreddit_name}/submit", response_model=SubmissionInfo, tags=["Submissions"])
async def submit_post(
    subreddit_name: str,
    submission_data: SubmissionCreate,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Submit a new post to a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)

        if submission_data.url:
            # Link submission
            submission = await subreddit.submit(
                title=submission_data.title,
                url=submission_data.url
            )
        else:
            # Text submission
            submission = await subreddit.submit(
                title=submission_data.title,
                selftext=submission_data.selftext or ""
            )

        await submission.load()

        return SubmissionInfo(
            id=submission.id,
            title=submission.title,
            author=submission.author.name if submission.author else "[deleted]",
            score=submission.score,
            url=submission.url,
            permalink=f"https://reddit.com{submission.permalink}",
            created_utc=submission.created_utc,
            num_comments=submission.num_comments,
            selftext=submission.selftext,
            is_self=submission.is_self,
            over_18=submission.over_18,
            subreddit=submission.subreddit.display_name
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to submit post: {str(e)}")


# Submission endpoints
@app.get("/submission/{submission_id}", response_model=SubmissionInfo, tags=["Submissions"])
async def get_submission(
    submission_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get information about a specific submission."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.load()

        return SubmissionInfo(
            id=submission.id,
            title=submission.title,
            author=submission.author.name if submission.author else "[deleted]",
            score=submission.score,
            url=submission.url,
            permalink=f"https://reddit.com{submission.permalink}",
            created_utc=submission.created_utc,
            num_comments=submission.num_comments,
            selftext=submission.selftext,
            is_self=submission.is_self,
            over_18=submission.over_18,
            subreddit=submission.subreddit.display_name
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to get submission: {str(e)}")


@app.get("/submission/{submission_id}/comments", response_model=List[CommentInfo], tags=["Comments"])
async def get_submission_comments(
    submission_id: str,
    limit: int = 100,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get comments for a submission."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.comments.replace_more(limit=0)

        comments = []
        for comment in submission.comments.list()[:limit]:
            if hasattr(comment, 'body'):  # Ensure it's a comment, not MoreComments
                comments.append(CommentInfo(
                    id=comment.id,
                    author=comment.author.name if comment.author else "[deleted]",
                    body=comment.body,
                    score=comment.score,
                    created_utc=comment.created_utc,
                    permalink=f"https://reddit.com{comment.permalink}",
                    is_submitter=comment.is_submitter,
                    parent_id=comment.parent_id,
                    submission_id=comment.submission.id
                ))

        return comments
    except Exception as e:
        raise RedditAPIException(f"Failed to get comments: {str(e)}")


@app.post("/submission/{submission_id}/comment", response_model=CommentInfo, tags=["Comments"])
async def comment_on_submission(
    submission_id: str,
    comment_data: CommentCreate,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Comment on a submission."""
    try:
        submission = await reddit.submission(submission_id)
        comment = await submission.reply(comment_data.body)
        await comment.load()

        return CommentInfo(
            id=comment.id,
            author=comment.author.name if comment.author else "[deleted]",
            body=comment.body,
            score=comment.score,
            created_utc=comment.created_utc,
            permalink=f"https://reddit.com{comment.permalink}",
            is_submitter=comment.is_submitter,
            parent_id=comment.parent_id,
            submission_id=comment.submission.id
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to comment on submission: {str(e)}")


# User endpoints
@app.get("/user/{username}", response_model=UserInfo, tags=["Users"])
async def get_user_info(
    username: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get information about a Reddit user."""
    try:
        redditor = await reddit.redditor(username)
        await redditor.load()

        return UserInfo(
            name=redditor.name,
            created_utc=redditor.created_utc,
            comment_karma=redditor.comment_karma,
            link_karma=redditor.link_karma,
            is_gold=redditor.is_gold,
            is_mod=redditor.is_mod,
            has_verified_email=redditor.has_verified_email
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to get user info: {str(e)}")


@app.get("/user/{username}/submissions", response_model=List[SubmissionInfo], tags=["Users"])
async def get_user_submissions(
    username: str,
    limit: int = 25,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get submissions by a user."""
    try:
        redditor = await reddit.redditor(username)
        submissions = []

        async for submission in redditor.submissions.new(limit=limit):
            submissions.append(SubmissionInfo(
                id=submission.id,
                title=submission.title,
                author=submission.author.name if submission.author else "[deleted]",
                score=submission.score,
                url=submission.url,
                permalink=f"https://reddit.com{submission.permalink}",
                created_utc=submission.created_utc,
                num_comments=submission.num_comments,
                selftext=submission.selftext,
                is_self=submission.is_self,
                over_18=submission.over_18,
                subreddit=submission.subreddit.display_name
            ))

        return submissions
    except Exception as e:
        raise RedditAPIException(f"Failed to get user submissions: {str(e)}")


# Search endpoints
@app.get("/search", response_model=List[SubmissionInfo], tags=["Search"])
async def search_reddit(
    query: str,
    subreddit: Optional[str] = None,
    sort: str = "relevance",
    time_filter: str = "all",
    limit: int = 25,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Search Reddit for submissions."""
    try:
        if subreddit:
            search_target = await reddit.subreddit(subreddit)
        else:
            search_target = reddit.subreddit("all")

        submissions = []
        async for submission in search_target.search(
            query, sort=sort, time_filter=time_filter, limit=limit
        ):
            submissions.append(SubmissionInfo(
                id=submission.id,
                title=submission.title,
                author=submission.author.name if submission.author else "[deleted]",
                score=submission.score,
                url=submission.url,
                permalink=f"https://reddit.com{submission.permalink}",
                created_utc=submission.created_utc,
                num_comments=submission.num_comments,
                selftext=submission.selftext,
                is_self=submission.is_self,
                over_18=submission.over_18,
                subreddit=submission.subreddit.display_name
            ))

        return submissions
    except Exception as e:
        raise RedditAPIException(f"Failed to search Reddit: {str(e)}")


# Front page endpoints
@app.get("/front/hot", response_model=List[SubmissionInfo], tags=["Front Page"])
async def get_front_page_hot(
    limit: int = 25,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get hot submissions from the front page."""
    try:
        submissions = []
        async for submission in reddit.front.hot(limit=limit):
            submissions.append(SubmissionInfo(
                id=submission.id,
                title=submission.title,
                author=submission.author.name if submission.author else "[deleted]",
                score=submission.score,
                url=submission.url,
                permalink=f"https://reddit.com{submission.permalink}",
                created_utc=submission.created_utc,
                num_comments=submission.num_comments,
                selftext=submission.selftext,
                is_self=submission.is_self,
                over_18=submission.over_18,
                subreddit=submission.subreddit.display_name
            ))

        return submissions
    except Exception as e:
        raise RedditAPIException(f"Failed to get front page: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)