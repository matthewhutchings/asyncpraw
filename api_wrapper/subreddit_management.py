"""
Subreddit management endpoints for Reddit API wrapper.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
import asyncpraw

from models import SubredditInfo
from auth import get_reddit_client
from exceptions import RedditAPIException

router = APIRouter()


@router.post("/subreddit/{subreddit_name}/subscribe", tags=["Subreddit Management"])
async def subscribe_to_subreddit(
    subreddit_name: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Subscribe to a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        await subreddit.subscribe()
        return {"message": f"Successfully subscribed to r/{subreddit_name}"}
    except Exception as e:
        raise RedditAPIException(f"Failed to subscribe to subreddit: {str(e)}")


@router.post("/subreddit/{subreddit_name}/unsubscribe", tags=["Subreddit Management"])
async def unsubscribe_from_subreddit(
    subreddit_name: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Unsubscribe from a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        await subreddit.unsubscribe()
        return {"message": f"Successfully unsubscribed from r/{subreddit_name}"}
    except Exception as e:
        raise RedditAPIException(f"Failed to unsubscribe from subreddit: {str(e)}")


@router.get("/subreddit/{subreddit_name}/rules", response_model=List[Dict[str, Any]], tags=["Subreddit Management"])
async def get_subreddit_rules(
    subreddit_name: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get rules for a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        rules_list = await subreddit.rules()

        rules = []
        for rule in rules_list:
            rules.append({
                "short_name": rule.short_name,
                "description": rule.description,
                "kind": rule.kind,
                "violation_reason": rule.violation_reason,
                "created_utc": rule.created_utc,
                "priority": rule.priority
            })

        return rules
    except Exception as e:
        raise RedditAPIException(f"Failed to get subreddit rules: {str(e)}")


@router.get("/subreddit/{subreddit_name}/wiki", response_model=List[str], tags=["Subreddit Management"])
async def get_subreddit_wiki_pages(
    subreddit_name: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get wiki pages for a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        pages = []

        async for page in subreddit.wiki:
            pages.append(page.name)

        return pages
    except Exception as e:
        raise RedditAPIException(f"Failed to get wiki pages: {str(e)}")


@router.get("/subreddit/{subreddit_name}/wiki/{page_name}", response_model=Dict[str, Any], tags=["Subreddit Management"])
async def get_wiki_page(
    subreddit_name: str,
    page_name: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get content of a specific wiki page."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        page = await subreddit.wiki[page_name]

        return {
            "name": page.name,
            "content_md": page.content_md,
            "content_html": page.content_html,
            "revision_date": page.revision_date,
            "revision_by": page.revision_by.name if page.revision_by else None,
            "may_revise": page.may_revise
        }
    except Exception as e:
        raise RedditAPIException(f"Failed to get wiki page: {str(e)}")


@router.get("/subreddit/{subreddit_name}/flair", response_model=List[Dict[str, Any]], tags=["Subreddit Management"])
async def get_subreddit_flairs(
    subreddit_name: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get available flairs for a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        flairs = []

        async for flair in subreddit.flair.link_templates:
            flairs.append({
                "id": flair.id,
                "text": flair.text,
                "css_class": flair.css_class,
                "text_editable": flair.text_editable,
                "background_color": flair.background_color,
                "text_color": flair.text_color,
                "mod_only": flair.mod_only,
                "allowable_content": flair.allowable_content,
                "max_emojis": flair.max_emojis
            })

        return flairs
    except Exception as e:
        raise RedditAPIException(f"Failed to get subreddit flairs: {str(e)}")


@router.get("/subreddit/{subreddit_name}/banned", response_model=List[str], tags=["Subreddit Management"])
async def get_banned_users(
    subreddit_name: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get banned users from a subreddit (requires mod permissions)."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        banned_users = []

        async for banned in subreddit.banned():
            banned_users.append(banned.name)

        return banned_users
    except Exception as e:
        raise RedditAPIException(f"Failed to get banned users: {str(e)}")


@router.get("/subreddit/{subreddit_name}/contributors", response_model=List[str], tags=["Subreddit Management"])
async def get_subreddit_contributors(
    subreddit_name: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get contributors of a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        contributors = []

        async for contributor in subreddit.contributor():
            contributors.append(contributor.name)

        return contributors
    except Exception as e:
        raise RedditAPIException(f"Failed to get contributors: {str(e)}")


@router.post("/subreddit/{subreddit_name}/user/{username}/ban", tags=["Subreddit Management"])
async def ban_user(
    subreddit_name: str,
    username: str,
    reason: Optional[str] = None,
    duration: Optional[int] = None,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Ban a user from a subreddit (requires mod permissions)."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        await subreddit.banned.add(username, ban_reason=reason, duration=duration)
        return {"message": f"User {username} banned from r/{subreddit_name}"}
    except Exception as e:
        raise RedditAPIException(f"Failed to ban user: {str(e)}")


@router.post("/subreddit/{subreddit_name}/user/{username}/unban", tags=["Subreddit Management"])
async def unban_user(
    subreddit_name: str,
    username: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Unban a user from a subreddit (requires mod permissions)."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        await subreddit.banned.remove(username)
        return {"message": f"User {username} unbanned from r/{subreddit_name}"}
    except Exception as e:
        raise RedditAPIException(f"Failed to unban user: {str(e)}")


@router.post("/subreddit/{subreddit_name}/user/{username}/add_contributor", tags=["Subreddit Management"])
async def add_contributor(
    subreddit_name: str,
    username: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Add a user as contributor to a subreddit (requires mod permissions)."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        await subreddit.contributor.add(username)
        return {"message": f"User {username} added as contributor to r/{subreddit_name}"}
    except Exception as e:
        raise RedditAPIException(f"Failed to add contributor: {str(e)}")


@router.post("/subreddit/{subreddit_name}/user/{username}/remove_contributor", tags=["Subreddit Management"])
async def remove_contributor(
    subreddit_name: str,
    username: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Remove a user as contributor from a subreddit (requires mod permissions)."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        await subreddit.contributor.remove(username)
        return {"message": f"User {username} removed as contributor from r/{subreddit_name}"}
    except Exception as e:
        raise RedditAPIException(f"Failed to remove contributor: {str(e)}")


@router.get("/subreddit/{subreddit_name}/modqueue", response_model=List[Dict[str, Any]], tags=["Subreddit Management"])
async def get_modqueue(
    subreddit_name: str,
    limit: int = Query(25, ge=1, le=100),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get items in moderation queue (requires mod permissions)."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        modqueue_items = []

        async for item in subreddit.mod.queue(limit=limit):
            item_data = {
                "id": item.id,
                "author": item.author.name if item.author else "[deleted]",
                "created_utc": item.created_utc,
                "num_reports": item.num_reports,
                "permalink": f"https://reddit.com{item.permalink}"
            }

            if hasattr(item, 'title'):  # Submission
                item_data.update({
                    "type": "submission",
                    "title": item.title,
                    "url": item.url
                })
            else:  # Comment
                item_data.update({
                    "type": "comment",
                    "body": item.body[:200] + "..." if len(item.body) > 200 else item.body
                })

            modqueue_items.append(item_data)

        return modqueue_items
    except Exception as e:
        raise RedditAPIException(f"Failed to get modqueue: {str(e)}")


@router.post("/subreddit/{subreddit_name}/approve/{item_id}", tags=["Subreddit Management"])
async def approve_item(
    subreddit_name: str,
    item_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Approve a submission or comment (requires mod permissions)."""
    try:
        # Try to get as submission first, then as comment
        try:
            item = await reddit.submission(item_id)
            await item.mod.approve()
        except:
            item = await reddit.comment(item_id)
            await item.mod.approve()

        return {"message": f"Item {item_id} approved in r/{subreddit_name}"}
    except Exception as e:
        raise RedditAPIException(f"Failed to approve item: {str(e)}")


@router.post("/subreddit/{subreddit_name}/remove/{item_id}", tags=["Subreddit Management"])
async def remove_item(
    subreddit_name: str,
    item_id: str,
    spam: bool = False,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Remove a submission or comment (requires mod permissions)."""
    try:
        # Try to get as submission first, then as comment
        try:
            item = await reddit.submission(item_id)
            await item.mod.remove(spam=spam)
        except:
            item = await reddit.comment(item_id)
            await item.mod.remove(spam=spam)

        return {"message": f"Item {item_id} removed from r/{subreddit_name}"}
    except Exception as e:
        raise RedditAPIException(f"Failed to remove item: {str(e)}")


@router.get("/subreddit/search", response_model=List[SubredditInfo], tags=["Subreddit Management"])
async def search_subreddits(
    query: str = Query(..., min_length=1),
    limit: int = Query(25, ge=1, le=100),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Search for subreddits."""
    try:
        subreddits = []

        async for subreddit in reddit.subreddits.search(query, limit=limit):
            subreddits.append(SubredditInfo(
                name=subreddit.display_name,
                title=subreddit.title,
                description=subreddit.public_description,
                subscribers=subreddit.subscribers,
                created_utc=subreddit.created_utc,
                over18=subreddit.over18,
                public_description=subreddit.public_description
            ))

        return subreddits
    except Exception as e:
        raise RedditAPIException(f"Failed to search subreddits: {str(e)}")


@router.get("/subreddits/popular", response_model=List[SubredditInfo], tags=["Subreddit Management"])
async def get_popular_subreddits(
    limit: int = Query(25, ge=1, le=100),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get popular subreddits."""
    try:
        subreddits = []

        async for subreddit in reddit.subreddits.popular(limit=limit):
            subreddits.append(SubredditInfo(
                name=subreddit.display_name,
                title=subreddit.title,
                description=subreddit.public_description,
                subscribers=subreddit.subscribers,
                created_utc=subreddit.created_utc,
                over18=subreddit.over18,
                public_description=subreddit.public_description
            ))

        return subreddits
    except Exception as e:
        raise RedditAPIException(f"Failed to get popular subreddits: {str(e)}")