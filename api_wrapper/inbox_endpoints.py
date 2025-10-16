"""
Inbox and Message Management endpoints for Reddit API wrapper.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import asyncpraw

from models import MessageInfo, MessageCreate, UserInfo
from auth import get_reddit_client
from exceptions import RedditAPIException

router = APIRouter()


@router.get("/inbox/all", response_model=List[MessageInfo], tags=["Inbox"])
async def get_inbox_all(
    limit: int = Query(25, ge=1, le=100),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get all inbox messages and comment replies."""
    try:
        messages = []
        async for item in reddit.inbox.all(limit=limit):
            if hasattr(item, 'body'):  # It's a message or comment
                messages.append(MessageInfo(
                    id=item.id,
                    author=item.author.name if item.author else "[deleted]",
                    body=item.body,
                    body_html=getattr(item, 'body_html', ''),
                    subject=getattr(item, 'subject', 'Comment Reply'),
                    created_utc=item.created_utc,
                    dest=getattr(item, 'dest', 'me'),
                    was_comment=getattr(item, 'was_comment', hasattr(item, 'submission')),
                    name=item.fullname,
                    subreddit=getattr(item, 'subreddit', None)
                ))
        return messages
    except Exception as e:
        raise RedditAPIException(f"Failed to get inbox: {str(e)}")


@router.get("/inbox/unread", response_model=List[MessageInfo], tags=["Inbox"])
async def get_inbox_unread(
    limit: int = Query(25, ge=1, le=100),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get unread inbox messages."""
    try:
        messages = []
        async for item in reddit.inbox.unread(limit=limit):
            if hasattr(item, 'body'):
                messages.append(MessageInfo(
                    id=item.id,
                    author=item.author.name if item.author else "[deleted]",
                    body=item.body,
                    body_html=getattr(item, 'body_html', ''),
                    subject=getattr(item, 'subject', 'Comment Reply'),
                    created_utc=item.created_utc,
                    dest=getattr(item, 'dest', 'me'),
                    was_comment=getattr(item, 'was_comment', hasattr(item, 'submission')),
                    name=item.fullname,
                    subreddit=getattr(item, 'subreddit', None)
                ))
        return messages
    except Exception as e:
        raise RedditAPIException(f"Failed to get unread inbox: {str(e)}")


@router.get("/inbox/mentions", response_model=List[MessageInfo], tags=["Inbox"])
async def get_inbox_mentions(
    limit: int = Query(25, ge=1, le=100),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get username mentions."""
    try:
        messages = []
        async for item in reddit.inbox.mentions(limit=limit):
            messages.append(MessageInfo(
                id=item.id,
                author=item.author.name if item.author else "[deleted]",
                body=item.body,
                body_html=getattr(item, 'body_html', ''),
                subject="Username Mention",
                created_utc=item.created_utc,
                dest="me",
                was_comment=True,
                name=item.fullname,
                subreddit=item.subreddit.display_name if item.subreddit else None
            ))
        return messages
    except Exception as e:
        raise RedditAPIException(f"Failed to get mentions: {str(e)}")


@router.get("/inbox/comment_replies", response_model=List[MessageInfo], tags=["Inbox"])
async def get_inbox_comment_replies(
    limit: int = Query(25, ge=1, le=100),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get comment replies."""
    try:
        messages = []
        async for item in reddit.inbox.comment_replies(limit=limit):
            messages.append(MessageInfo(
                id=item.id,
                author=item.author.name if item.author else "[deleted]",
                body=item.body,
                body_html=getattr(item, 'body_html', ''),
                subject="Comment Reply",
                created_utc=item.created_utc,
                dest="me",
                was_comment=True,
                name=item.fullname,
                subreddit=item.subreddit.display_name if item.subreddit else None
            ))
        return messages
    except Exception as e:
        raise RedditAPIException(f"Failed to get comment replies: {str(e)}")


@router.get("/inbox/submission_replies", response_model=List[MessageInfo], tags=["Inbox"])
async def get_inbox_submission_replies(
    limit: int = Query(25, ge=1, le=100),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get submission replies."""
    try:
        messages = []
        async for item in reddit.inbox.submission_replies(limit=limit):
            messages.append(MessageInfo(
                id=item.id,
                author=item.author.name if item.author else "[deleted]",
                body=item.body,
                body_html=getattr(item, 'body_html', ''),
                subject="Submission Reply",
                created_utc=item.created_utc,
                dest="me",
                was_comment=True,
                name=item.fullname,
                subreddit=item.subreddit.display_name if item.subreddit else None
            ))
        return messages
    except Exception as e:
        raise RedditAPIException(f"Failed to get submission replies: {str(e)}")


@router.post("/message/send", tags=["Messages"])
async def send_message(
    message_data: MessageCreate,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Send a private message to a user."""
    try:
        if message_data.from_subreddit:
            subreddit = await reddit.subreddit(message_data.from_subreddit)
            await subreddit.message(
                subject=message_data.subject,
                message=message_data.message
            )
        else:
            redditor = await reddit.redditor(message_data.to)
            await redditor.message(
                subject=message_data.subject,
                message=message_data.message
            )
        return {"message": "Message sent successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to send message: {str(e)}")


@router.post("/message/{message_id}/delete", tags=["Messages"])
async def delete_message(
    message_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Delete a message."""
    try:
        # Get the message first
        async for message in reddit.inbox.all(limit=100):
            if message.id == message_id:
                await message.delete()
                return {"message": "Message deleted successfully"}
        raise HTTPException(status_code=404, detail="Message not found")
    except Exception as e:
        raise RedditAPIException(f"Failed to delete message: {str(e)}")


@router.post("/message/{message_id}/mark_read", tags=["Messages"])
async def mark_message_read(
    message_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Mark a message as read."""
    try:
        # Get the message first
        async for message in reddit.inbox.unread(limit=100):
            if message.id == message_id:
                await message.mark_read()
                return {"message": "Message marked as read"}
        raise HTTPException(status_code=404, detail="Message not found or already read")
    except Exception as e:
        raise RedditAPIException(f"Failed to mark message as read: {str(e)}")


@router.post("/message/{message_id}/mark_unread", tags=["Messages"])
async def mark_message_unread(
    message_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Mark a message as unread."""
    try:
        # Get the message first
        async for message in reddit.inbox.all(limit=100):
            if message.id == message_id:
                await message.mark_unread()
                return {"message": "Message marked as unread"}
        raise HTTPException(status_code=404, detail="Message not found")
    except Exception as e:
        raise RedditAPIException(f"Failed to mark message as unread: {str(e)}")


@router.post("/user/{username}/block", tags=["User Management"])
async def block_user(
    username: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Block a user."""
    try:
        redditor = await reddit.redditor(username)
        await redditor.block()
        return {"message": f"User {username} blocked successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to block user: {str(e)}")


@router.post("/inbox/mark_all_read", tags=["Inbox"])
async def mark_all_inbox_read(
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Mark all inbox messages as read."""
    try:
        await reddit.inbox.mark_all_read()
        return {"message": "All inbox messages marked as read"}
    except Exception as e:
        raise RedditAPIException(f"Failed to mark all messages as read: {str(e)}")