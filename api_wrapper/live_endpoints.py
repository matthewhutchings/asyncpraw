"""
Live thread management endpoints for Reddit API wrapper.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
import asyncpraw

from models import LiveThreadInfo, LiveThreadCreate
from auth import get_reddit_client
from exceptions import RedditAPIException

router = APIRouter()


@router.post("/live/create", response_model=LiveThreadInfo, tags=["Live Threads"])
async def create_live_thread(
    live_data: LiveThreadCreate,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Create a new live thread."""
    try:
        live_thread = await reddit.live.create(
            title=live_data.title,
            description=live_data.description,
            nsfw=live_data.nsfw
        )
        await live_thread.load()

        return LiveThreadInfo(
            id=live_thread.id,
            title=live_thread.title,
            description=live_thread.description,
            created_utc=live_thread.created_utc,
            state=live_thread.state,
            viewer_count=live_thread.viewer_count,
            viewer_count_fuzzed=live_thread.viewer_count_fuzzed
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to create live thread: {str(e)}")


@router.get("/live/{thread_id}", response_model=LiveThreadInfo, tags=["Live Threads"])
async def get_live_thread(
    thread_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get information about a live thread."""
    try:
        live_thread = await reddit.live(thread_id)
        await live_thread.load()

        return LiveThreadInfo(
            id=live_thread.id,
            title=live_thread.title,
            description=live_thread.description,
            created_utc=live_thread.created_utc,
            state=live_thread.state,
            viewer_count=live_thread.viewer_count,
            viewer_count_fuzzed=live_thread.viewer_count_fuzzed
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to get live thread: {str(e)}")


@router.post("/live/{thread_id}/update", tags=["Live Threads"])
async def add_live_update(
    thread_id: str,
    body: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Add an update to a live thread."""
    try:
        live_thread = await reddit.live(thread_id)
        update = await live_thread.add_update(body)
        return {
            "message": "Live update added successfully",
            "update_id": update.id if update else None
        }
    except Exception as e:
        raise RedditAPIException(f"Failed to add live update: {str(e)}")


@router.get("/live/{thread_id}/updates", response_model=List[Dict[str, Any]], tags=["Live Threads"])
async def get_live_updates(
    thread_id: str,
    limit: int = 25,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get updates from a live thread."""
    try:
        live_thread = await reddit.live(thread_id)
        updates = []

        async for update in live_thread.updates(limit=limit):
            updates.append({
                "id": update.id,
                "author": update.author.name if update.author else "[deleted]",
                "body": update.body,
                "created_utc": update.created_utc,
                "embeds": getattr(update, 'embeds', []),
                "stricken": getattr(update, 'stricken', False)
            })

        return updates
    except Exception as e:
        raise RedditAPIException(f"Failed to get live updates: {str(e)}")


@router.post("/live/{thread_id}/close", tags=["Live Threads"])
async def close_live_thread(
    thread_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Close a live thread."""
    try:
        live_thread = await reddit.live(thread_id)
        await live_thread.close()
        return {"message": "Live thread closed successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to close live thread: {str(e)}")


@router.get("/live/{thread_id}/contributors", response_model=List[str], tags=["Live Threads"])
async def get_live_contributors(
    thread_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get contributors of a live thread."""
    try:
        live_thread = await reddit.live(thread_id)
        contributors = []

        async for contributor in live_thread.contributor():
            contributors.append(contributor.name)

        return contributors
    except Exception as e:
        raise RedditAPIException(f"Failed to get live contributors: {str(e)}")


@router.post("/live/{thread_id}/contributors/{username}/invite", tags=["Live Threads"])
async def invite_live_contributor(
    thread_id: str,
    username: str,
    permissions: List[str] = None,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Invite a user to contribute to a live thread."""
    try:
        live_thread = await reddit.live(thread_id)
        await live_thread.contributor.invite(username, permissions=permissions)
        return {"message": f"Invited {username} to contribute to live thread"}
    except Exception as e:
        raise RedditAPIException(f"Failed to invite contributor: {str(e)}")


@router.post("/live/{thread_id}/contributors/{username}/remove", tags=["Live Threads"])
async def remove_live_contributor(
    thread_id: str,
    username: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Remove a contributor from a live thread."""
    try:
        live_thread = await reddit.live(thread_id)
        await live_thread.contributor.remove(username)
        return {"message": f"Removed {username} from live thread contributors"}
    except Exception as e:
        raise RedditAPIException(f"Failed to remove contributor: {str(e)}")


@router.post("/live/{thread_id}/accept_invitation", tags=["Live Threads"])
async def accept_live_invitation(
    thread_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Accept an invitation to contribute to a live thread."""
    try:
        live_thread = await reddit.live(thread_id)
        await live_thread.contributor.accept_invite()
        return {"message": "Live thread invitation accepted"}
    except Exception as e:
        raise RedditAPIException(f"Failed to accept invitation: {str(e)}")


@router.post("/live/{thread_id}/leave", tags=["Live Threads"])
async def leave_live_thread(
    thread_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Leave a live thread as a contributor."""
    try:
        live_thread = await reddit.live(thread_id)
        await live_thread.contributor.leave()
        return {"message": "Left live thread as contributor"}
    except Exception as e:
        raise RedditAPIException(f"Failed to leave live thread: {str(e)}")


@router.get("/live/{thread_id}/discussions", response_model=List[Dict[str, Any]], tags=["Live Threads"])
async def get_live_discussions(
    thread_id: str,
    limit: int = 25,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get discussions related to a live thread."""
    try:
        live_thread = await reddit.live(thread_id)
        discussions = []

        async for submission in live_thread.discussions(limit=limit):
            discussions.append({
                "id": submission.id,
                "title": submission.title,
                "author": submission.author.name if submission.author else "[deleted]",
                "score": submission.score,
                "url": submission.url,
                "permalink": f"https://reddit.com{submission.permalink}",
                "created_utc": submission.created_utc,
                "num_comments": submission.num_comments,
                "subreddit": submission.subreddit.display_name
            })

        return discussions
    except Exception as e:
        raise RedditAPIException(f"Failed to get live discussions: {str(e)}")


@router.post("/live/{thread_id}/strike_update/{update_id}", tags=["Live Threads"])
async def strike_live_update(
    thread_id: str,
    update_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Strike (mark as incorrect) a live update."""
    try:
        live_thread = await reddit.live(thread_id)
        update = await live_thread.update(update_id)
        await update.strike()
        return {"message": "Live update struck successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to strike update: {str(e)}")