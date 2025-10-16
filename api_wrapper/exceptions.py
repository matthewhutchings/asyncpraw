"""
Custom exceptions for the Reddit API wrapper.
"""

from fastapi import status


class RedditAPIException(Exception):
    """Custom exception for Reddit API errors."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, detail: str = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)


class AuthenticationError(RedditAPIException):
    """Exception raised when Reddit authentication fails."""

    def __init__(self, message: str = "Reddit authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class RateLimitError(RedditAPIException):
    """Exception raised when Reddit API rate limit is exceeded."""

    def __init__(self, message: str = "Reddit API rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)


class PermissionError(RedditAPIException):
    """Exception raised when user lacks permissions for an action."""

    def __init__(self, message: str = "Insufficient permissions for this action"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundError(RedditAPIException):
    """Exception raised when a Reddit resource is not found."""

    def __init__(self, message: str = "Reddit resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)