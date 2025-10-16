"""
Inbox toggles and settings management for Reddit API wrapper.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
import asyncpraw

from auth import get_reddit_client
from exceptions import RedditAPIException

router = APIRouter()


@router.post("/comment/{comment_id}/enable_inbox_replies", tags=["Inbox Settings"])
async def enable_comment_inbox_replies(
    comment_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Enable inbox replies for a comment."""
    try:
        comment = await reddit.comment(comment_id)
        await comment.enable_inbox_replies()
        return {"message": "Inbox replies enabled for comment"}
    except Exception as e:
        raise RedditAPIException(f"Failed to enable inbox replies: {str(e)}")


@router.post("/comment/{comment_id}/disable_inbox_replies", tags=["Inbox Settings"])
async def disable_comment_inbox_replies(
    comment_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Disable inbox replies for a comment."""
    try:
        comment = await reddit.comment(comment_id)
        await comment.disable_inbox_replies()
        return {"message": "Inbox replies disabled for comment"}
    except Exception as e:
        raise RedditAPIException(f"Failed to disable inbox replies: {str(e)}")


@router.post("/submission/{submission_id}/enable_inbox_replies", tags=["Inbox Settings"])
async def enable_submission_inbox_replies(
    submission_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Enable inbox replies for a submission."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.enable_inbox_replies()
        return {"message": "Inbox replies enabled for submission"}
    except Exception as e:
        raise RedditAPIException(f"Failed to enable inbox replies: {str(e)}")


@router.post("/submission/{submission_id}/disable_inbox_replies", tags=["Inbox Settings"])
async def disable_submission_inbox_replies(
    submission_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Disable inbox replies for a submission."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.disable_inbox_replies()
        return {"message": "Inbox replies disabled for submission"}
    except Exception as e:
        raise RedditAPIException(f"Failed to disable inbox replies: {str(e)}")


@router.get("/user/preferences", response_model=Dict[str, Any], tags=["User Settings"])
async def get_user_preferences(
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get user preferences."""
    try:
        preferences = await reddit.user.preferences()
        return preferences.__dict__
    except Exception as e:
        raise RedditAPIException(f"Failed to get user preferences: {str(e)}")


@router.patch("/user/preferences", tags=["User Settings"])
async def update_user_preferences(
    preferences: Dict[str, Any],
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Update user preferences."""
    try:
        current_prefs = await reddit.user.preferences()
        await current_prefs.update(**preferences)
        return {"message": "User preferences updated successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to update user preferences: {str(e)}")


@router.get("/user/karma", response_model=Dict[str, int], tags=["User Settings"])
async def get_user_karma_breakdown(
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get karma breakdown by subreddit."""
    try:
        karma_list = await reddit.user.karma()
        karma_dict = {}
        for karma_item in karma_list:
            subreddit_name = karma_item['sr']
            karma_dict[subreddit_name] = {
                'comment_karma': karma_item['comment_karma'],
                'link_karma': karma_item['link_karma']
            }
        return karma_dict
    except Exception as e:
        raise RedditAPIException(f"Failed to get karma breakdown: {str(e)}")


@router.get("/user/friends", response_model=List[str], tags=["User Settings"])
async def get_friends(
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get list of friends."""
    try:
        friends = []
        async for friend in reddit.user.friends():
            friends.append(friend.name)
        return friends
    except Exception as e:
        raise RedditAPIException(f"Failed to get friends list: {str(e)}")


@router.post("/user/{username}/friend", tags=["User Settings"])
async def add_friend(
    username: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Add a user as friend."""
    try:
        redditor = await reddit.redditor(username)
        await redditor.friend()
        return {"message": f"Added {username} as friend"}
    except Exception as e:
        raise RedditAPIException(f"Failed to add friend: {str(e)}")


@router.delete("/user/{username}/friend", tags=["User Settings"])
async def remove_friend(
    username: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Remove a user from friends."""
    try:
        redditor = await reddit.redditor(username)
        await redditor.unfriend()
        return {"message": f"Removed {username} from friends"}
    except Exception as e:
        raise RedditAPIException(f"Failed to remove friend: {str(e)}")


@router.get("/user/blocked", response_model=List[str], tags=["User Settings"])
async def get_blocked_users(
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get list of blocked users."""
    try:
        blocked = []
        async for blocked_user in reddit.user.blocked():
            blocked.append(blocked_user.name)
        return blocked
    except Exception as e:
        raise RedditAPIException(f"Failed to get blocked users: {str(e)}")


@router.post("/user/{username}/unblock", tags=["User Settings"])
async def unblock_user(
    username: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Unblock a user."""
    try:
        redditor = await reddit.redditor(username)
        await redditor.unblock()
        return {"message": f"Unblocked user {username}"}
    except Exception as e:
        raise RedditAPIException(f"Failed to unblock user: {str(e)}")


@router.get("/user/multireddits", response_model=List[Dict[str, Any]], tags=["User Settings"])
async def get_multireddits(
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get user's multireddits."""
    try:
        multireddits = []
        async for multireddit in reddit.user.multireddits():
            multireddits.append({
                'name': multireddit.name,
                'display_name': multireddit.display_name,
                'description_md': multireddit.description_md,
                'subreddits': [sub.display_name for sub in multireddit.subreddits],
                'visibility': multireddit.visibility,
                'created_utc': multireddit.created_utc
            })
        return multireddits
    except Exception as e:
        raise RedditAPIException(f"Failed to get multireddits: {str(e)}")


@router.get("/user/subreddits", response_model=List[str], tags=["User Settings"])
async def get_user_subreddits(
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get subreddits the user is subscribed to."""
    try:
        subreddits = []
        async for subreddit in reddit.user.subreddits():
            subreddits.append(subreddit.display_name)
        return subreddits
    except Exception as e:
        raise RedditAPIException(f"Failed to get user subreddits: {str(e)}")


@router.get("/user/contributor_subreddits", response_model=List[str], tags=["User Settings"])
async def get_contributor_subreddits(
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get subreddits where the user is a contributor."""
    try:
        subreddits = []
        async for subreddit in reddit.user.contributor_subreddits():
            subreddits.append(subreddit.display_name)
        return subreddits
    except Exception as e:
        raise RedditAPIException(f"Failed to get contributor subreddits: {str(e)}")


@router.get("/user/moderator_subreddits", response_model=List[str], tags=["User Settings"])
async def get_moderator_subreddits(
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get subreddits where the user is a moderator."""
    try:
        subreddits = []
        async for subreddit in reddit.user.moderator_subreddits():
            subreddits.append(subreddit.display_name)
        return subreddits
    except Exception as e:
        raise RedditAPIException(f"Failed to get moderator subreddits: {str(e)}")