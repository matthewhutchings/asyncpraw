"""
Pydantic models for API request/response schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SubredditInfo(BaseModel):
    """Information about a subreddit."""
    name: str = Field(..., description="Subreddit name")
    title: str = Field(..., description="Subreddit title")
    description: str = Field(..., description="Subreddit description")
    subscribers: int = Field(..., description="Number of subscribers")
    created_utc: float = Field(..., description="Creation timestamp")
    over18: bool = Field(..., description="Whether subreddit is NSFW")
    public_description: str = Field(..., description="Public description")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "python",
                "title": "Python Programming",
                "description": "News about the programming language Python",
                "subscribers": 1000000,
                "created_utc": 1202144728.0,
                "over18": False,
                "public_description": "News about the programming language Python"
            }
        }


class SubmissionInfo(BaseModel):
    """Information about a Reddit submission."""
    id: str = Field(..., description="Submission ID")
    title: str = Field(..., description="Submission title")
    author: str = Field(..., description="Author username")
    score: int = Field(..., description="Submission score")
    url: str = Field(..., description="Submission URL")
    permalink: str = Field(..., description="Reddit permalink")
    created_utc: float = Field(..., description="Creation timestamp")
    num_comments: int = Field(..., description="Number of comments")
    selftext: str = Field(..., description="Self text content")
    is_self: bool = Field(..., description="Whether it's a self post")
    over_18: bool = Field(..., description="Whether it's NSFW")
    subreddit: str = Field(..., description="Subreddit name")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "title": "Example Post Title",
                "author": "example_user",
                "score": 100,
                "url": "https://example.com",
                "permalink": "https://reddit.com/r/example/comments/abc123/example_post/",
                "created_utc": 1640995200.0,
                "num_comments": 50,
                "selftext": "This is example text content",
                "is_self": True,
                "over_18": False,
                "subreddit": "example"
            }
        }


class SubmissionCreate(BaseModel):
    """Data for creating a new submission."""
    title: str = Field(..., min_length=1, max_length=300, description="Submission title")
    selftext: Optional[str] = Field(None, description="Text content for self posts")
    url: Optional[str] = Field(None, description="URL for link posts")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Check out this cool Python library",
                "url": "https://github.com/example/library"
            }
        }


class CommentInfo(BaseModel):
    """Information about a Reddit comment."""
    id: str = Field(..., description="Comment ID")
    author: str = Field(..., description="Author username")
    body: str = Field(..., description="Comment content")
    score: int = Field(..., description="Comment score")
    created_utc: float = Field(..., description="Creation timestamp")
    permalink: str = Field(..., description="Reddit permalink")
    is_submitter: bool = Field(..., description="Whether author is OP")
    parent_id: str = Field(..., description="Parent comment/submission ID")
    submission_id: str = Field(..., description="Submission ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "xyz789",
                "author": "commenter",
                "body": "This is a great post!",
                "score": 25,
                "created_utc": 1640995800.0,
                "permalink": "https://reddit.com/r/example/comments/abc123/example_post/xyz789/",
                "is_submitter": False,
                "parent_id": "t3_abc123",
                "submission_id": "abc123"
            }
        }


class CommentCreate(BaseModel):
    """Data for creating a new comment."""
    body: str = Field(..., min_length=1, description="Comment text")

    class Config:
        json_schema_extra = {
            "example": {
                "body": "Thanks for sharing this!"
            }
        }


class UserInfo(BaseModel):
    """Information about a Reddit user."""
    name: str = Field(..., description="Username")
    created_utc: float = Field(..., description="Account creation timestamp")
    comment_karma: int = Field(..., description="Comment karma")
    link_karma: int = Field(..., description="Link karma")
    is_gold: bool = Field(..., description="Whether user has Reddit Gold")
    is_mod: bool = Field(..., description="Whether user is a moderator")
    has_verified_email: bool = Field(..., description="Whether email is verified")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "example_user",
                "created_utc": 1234567890.0,
                "comment_karma": 5000,
                "link_karma": 1000,
                "is_gold": False,
                "is_mod": True,
                "has_verified_email": True
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    detail: str = Field(..., description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Authentication Failed",
                "detail": "Invalid Reddit credentials provided"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "Reddit API Wrapper"
            }
        }


class MessageInfo(BaseModel):
    """Information about a Reddit message."""
    id: str = Field(..., description="Message ID")
    author: str = Field(..., description="Author username")
    body: str = Field(..., description="Message content")
    body_html: str = Field(..., description="Message content as HTML")
    subject: str = Field(..., description="Message subject")
    created_utc: float = Field(..., description="Creation timestamp")
    dest: str = Field(..., description="Recipient username")
    was_comment: bool = Field(..., description="Whether message was a comment reply")
    name: str = Field(..., description="Full ID with prefix")
    subreddit: Optional[str] = Field(None, description="Subreddit if subreddit message")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg123",
                "author": "sender_user",
                "body": "Hello there!",
                "body_html": "&lt;div class=\"md\"&gt;&lt;p&gt;Hello there!&lt;/p&gt;&lt;/div&gt;",
                "subject": "Test Message",
                "created_utc": 1640995200.0,
                "dest": "recipient_user",
                "was_comment": False,
                "name": "t4_msg123",
                "subreddit": None
            }
        }


class MessageCreate(BaseModel):
    """Data for creating a new message."""
    to: str = Field(..., description="Recipient username")
    subject: str = Field(..., min_length=1, max_length=100, description="Message subject")
    message: str = Field(..., min_length=1, description="Message body")
    from_subreddit: Optional[str] = Field(None, description="Send from subreddit")

    class Config:
        json_schema_extra = {
            "example": {
                "to": "recipient_user",
                "subject": "Hello",
                "message": "This is a test message!"
            }
        }


class DraftInfo(BaseModel):
    """Information about a Reddit draft."""
    id: str = Field(..., description="Draft ID")
    title: str = Field(..., description="Draft title")
    selftext: str = Field(..., description="Draft content")
    subreddit: str = Field(..., description="Target subreddit")
    kind: str = Field(..., description="Draft type (self, link, etc.)")
    url: Optional[str] = Field(None, description="URL for link drafts")
    created_utc: float = Field(..., description="Creation timestamp")
    is_public_link: bool = Field(..., description="Whether link is public")
    send_replies: bool = Field(..., description="Whether to send replies")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "draft123",
                "title": "My Draft Post",
                "selftext": "This is draft content",
                "subreddit": "test",
                "kind": "self",
                "url": None,
                "created_utc": 1640995200.0,
                "is_public_link": True,
                "send_replies": True
            }
        }


class DraftCreate(BaseModel):
    """Data for creating a new draft."""
    title: str = Field(..., min_length=1, max_length=300, description="Draft title")
    selftext: Optional[str] = Field("", description="Text content")
    url: Optional[str] = Field(None, description="URL for link posts")
    subreddit: str = Field(..., description="Target subreddit")
    send_replies: bool = Field(True, description="Send replies")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My Draft Title",
                "selftext": "This is my draft content",
                "subreddit": "test"
            }
        }


class DraftUpdate(BaseModel):
    """Data for updating a draft."""
    title: Optional[str] = Field(None, min_length=1, max_length=300, description="Draft title")
    selftext: Optional[str] = Field(None, description="Text content")
    url: Optional[str] = Field(None, description="URL for link posts")
    subreddit: Optional[str] = Field(None, description="Target subreddit")
    send_replies: Optional[bool] = Field(None, description="Send replies")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Draft Title",
                "selftext": "Updated content"
            }
        }


class PollSubmissionCreate(BaseModel):
    """Data for creating a poll submission."""
    title: str = Field(..., min_length=1, max_length=300, description="Poll title")
    selftext: str = Field("", description="Poll description")
    options: List[str] = Field(..., min_items=2, max_items=6, description="Poll options")
    duration: int = Field(..., ge=1, le=7, description="Poll duration in days")
    flair_id: Optional[str] = Field(None, description="Flair template ID")
    flair_text: Optional[str] = Field(None, description="Custom flair text")
    nsfw: bool = Field(False, description="Mark as NSFW")
    spoiler: bool = Field(False, description="Mark as spoiler")
    send_replies: bool = Field(True, description="Send replies")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "What's your favorite programming language?",
                "selftext": "Vote for your favorite!",
                "options": ["Python", "JavaScript", "Go", "Rust"],
                "duration": 3
            }
        }


class GallerySubmissionCreate(BaseModel):
    """Data for creating a gallery submission."""
    title: str = Field(..., min_length=1, max_length=300, description="Gallery title")
    images: List[dict] = Field(..., min_items=1, max_items=20, description="Image data")
    flair_id: Optional[str] = Field(None, description="Flair template ID")
    flair_text: Optional[str] = Field(None, description="Custom flair text")
    nsfw: bool = Field(False, description="Mark as NSFW")
    spoiler: bool = Field(False, description="Mark as spoiler")
    send_replies: bool = Field(True, description="Send replies")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My Photo Gallery",
                "images": [
                    {"image_path": "/path/to/image1.jpg", "caption": "First image"},
                    {"image_path": "/path/to/image2.jpg", "caption": "Second image"}
                ]
            }
        }


class LiveThreadInfo(BaseModel):
    """Information about a live thread."""
    id: str = Field(..., description="Live thread ID")
    title: str = Field(..., description="Live thread title")
    description: str = Field(..., description="Live thread description")
    created_utc: float = Field(..., description="Creation timestamp")
    state: str = Field(..., description="Thread state (live, complete, etc.)")
    viewer_count: int = Field(..., description="Number of viewers")
    viewer_count_fuzzed: bool = Field(..., description="Whether viewer count is fuzzed")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "live123",
                "title": "Breaking News Event",
                "description": "Live updates on the event",
                "created_utc": 1640995200.0,
                "state": "live",
                "viewer_count": 1500,
                "viewer_count_fuzzed": True
            }
        }


class LiveThreadCreate(BaseModel):
    """Data for creating a live thread."""
    title: str = Field(..., min_length=1, max_length=120, description="Live thread title")
    description: Optional[str] = Field("", description="Live thread description")
    nsfw: bool = Field(False, description="Mark as NSFW")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Live Event Updates",
                "description": "Following the live event"
            }
        }