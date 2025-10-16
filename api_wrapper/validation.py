"""
Input validation and error handling utilities.
"""

import re
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from pydantic import ValidationError


def validate_subreddit_name(name: str) -> bool:
    """
    Validate subreddit name format.

    Args:
        name: Subreddit name to validate

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If invalid
    """
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subreddit name cannot be empty"
        )

    if len(name) > 21:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subreddit name cannot be longer than 21 characters"
        )

    if not re.match(r'^[A-Za-z0-9_]+$', name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subreddit name can only contain letters, numbers, and underscores"
        )

    return True


def validate_username(username: str) -> bool:
    """
    Validate Reddit username format.

    Args:
        username: Username to validate

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If invalid
    """
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot be empty"
        )

    if len(username) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot be longer than 20 characters"
        )

    if not re.match(r'^[A-Za-z0-9_-]+$', username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username can only contain letters, numbers, underscores, and hyphens"
        )

    return True


def validate_submission_id(submission_id: str) -> bool:
    """
    Validate Reddit submission ID format.

    Args:
        submission_id: Submission ID to validate

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If invalid
    """
    if not submission_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission ID cannot be empty"
        )

    if not re.match(r'^[a-z0-9]+$', submission_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid submission ID format"
        )

    return True


def validate_comment_id(comment_id: str) -> bool:
    """
    Validate Reddit comment ID format.

    Args:
        comment_id: Comment ID to validate

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If invalid
    """
    if not comment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment ID cannot be empty"
        )

    if not re.match(r'^[a-z0-9]+$', comment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid comment ID format"
        )

    return True


def validate_post_title(title: str) -> bool:
    """
    Validate Reddit post title.

    Args:
        title: Post title to validate

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If invalid
    """
    if not title or not title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post title cannot be empty"
        )

    if len(title) > 300:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post title cannot be longer than 300 characters"
        )

    return True


def validate_comment_body(body: str) -> bool:
    """
    Validate comment body text.

    Args:
        body: Comment body to validate

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If invalid
    """
    if not body or not body.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment body cannot be empty"
        )

    if len(body) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment body cannot be longer than 10,000 characters"
        )

    return True


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If invalid
    """
    if not url:
        return True  # URL is optional

    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not url_pattern.match(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format"
        )

    return True


def validate_limit(limit: int, max_limit: int = 100) -> bool:
    """
    Validate limit parameter.

    Args:
        limit: Limit value to validate
        max_limit: Maximum allowed limit

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If invalid
    """
    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be at least 1"
        )

    if limit > max_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limit cannot exceed {max_limit}"
        )

    return True


def validate_time_filter(time_filter: str) -> bool:
    """
    Validate time filter parameter.

    Args:
        time_filter: Time filter to validate

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If invalid
    """
    valid_filters = {"hour", "day", "week", "month", "year", "all"}

    if time_filter not in valid_filters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid time filter. Must be one of: {', '.join(valid_filters)}"
        )

    return True


def validate_sort_method(sort_method: str) -> bool:
    """
    Validate sort method parameter.

    Args:
        sort_method: Sort method to validate

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If invalid
    """
    valid_sorts = {"relevance", "hot", "top", "new", "comments"}

    if sort_method not in valid_sorts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort method. Must be one of: {', '.join(valid_sorts)}"
        )

    return True


def handle_validation_error(exc: ValidationError) -> HTTPException:
    """
    Convert Pydantic validation errors to HTTP exceptions.

    Args:
        exc: Pydantic ValidationError

    Returns:
        HTTPException: Formatted HTTP exception
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"Validation errors: {'; '.join(errors)}"
    )