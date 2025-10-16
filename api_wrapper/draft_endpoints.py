"""
Draft management endpoints for Reddit API wrapper.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
import asyncpraw

from models import DraftInfo, DraftCreate, DraftUpdate, SubmissionInfo
from auth import get_reddit_client
from exceptions import RedditAPIException

router = APIRouter()


@router.get("/drafts", response_model=List[DraftInfo], tags=["Drafts"])
async def get_drafts(
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get all drafts for the authenticated user."""
    try:
        drafts = []
        async for draft in reddit.drafts():
            drafts.append(DraftInfo(
                id=draft.id,
                title=draft.title,
                selftext=draft.selftext,
                subreddit=draft.subreddit.display_name if draft.subreddit else "",
                kind=getattr(draft, 'kind', 'self'),
                url=getattr(draft, 'url', None),
                created_utc=getattr(draft, 'created_utc', 0),
                is_public_link=getattr(draft, 'is_public_link', True),
                send_replies=getattr(draft, 'send_replies', True)
            ))
        return drafts
    except Exception as e:
        raise RedditAPIException(f"Failed to get drafts: {str(e)}")


@router.get("/drafts/{draft_id}", response_model=DraftInfo, tags=["Drafts"])
async def get_draft(
    draft_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get a specific draft by ID."""
    try:
        draft = await reddit.drafts(draft_id)
        await draft.load()

        return DraftInfo(
            id=draft.id,
            title=draft.title,
            selftext=draft.selftext,
            subreddit=draft.subreddit.display_name if draft.subreddit else "",
            kind=getattr(draft, 'kind', 'self'),
            url=getattr(draft, 'url', None),
            created_utc=getattr(draft, 'created_utc', 0),
            is_public_link=getattr(draft, 'is_public_link', True),
            send_replies=getattr(draft, 'send_replies', True)
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to get draft: {str(e)}")


@router.post("/drafts", response_model=DraftInfo, tags=["Drafts"])
async def create_draft(
    draft_data: DraftCreate,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Create a new draft."""
    try:
        draft = await reddit.drafts.create(
            title=draft_data.title,
            selftext=draft_data.selftext,
            url=draft_data.url,
            subreddit=draft_data.subreddit,
            send_replies=draft_data.send_replies
        )
        await draft.load()

        return DraftInfo(
            id=draft.id,
            title=draft.title,
            selftext=draft.selftext,
            subreddit=draft.subreddit.display_name if draft.subreddit else "",
            kind=getattr(draft, 'kind', 'self'),
            url=getattr(draft, 'url', None),
            created_utc=getattr(draft, 'created_utc', 0),
            is_public_link=getattr(draft, 'is_public_link', True),
            send_replies=getattr(draft, 'send_replies', True)
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to create draft: {str(e)}")


@router.put("/drafts/{draft_id}", response_model=DraftInfo, tags=["Drafts"])
async def update_draft(
    draft_id: str,
    update_data: DraftUpdate,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Update an existing draft."""
    try:
        draft = await reddit.drafts(draft_id)

        # Prepare update data
        update_kwargs = {}
        if update_data.title is not None:
            update_kwargs['title'] = update_data.title
        if update_data.selftext is not None:
            update_kwargs['selftext'] = update_data.selftext
        if update_data.url is not None:
            update_kwargs['url'] = update_data.url
        if update_data.subreddit is not None:
            update_kwargs['subreddit'] = update_data.subreddit
        if update_data.send_replies is not None:
            update_kwargs['send_replies'] = update_data.send_replies

        updated_draft = await draft.update(**update_kwargs)
        await updated_draft.load()

        return DraftInfo(
            id=updated_draft.id,
            title=updated_draft.title,
            selftext=updated_draft.selftext,
            subreddit=updated_draft.subreddit.display_name if updated_draft.subreddit else "",
            kind=getattr(updated_draft, 'kind', 'self'),
            url=getattr(updated_draft, 'url', None),
            created_utc=getattr(updated_draft, 'created_utc', 0),
            is_public_link=getattr(updated_draft, 'is_public_link', True),
            send_replies=getattr(updated_draft, 'send_replies', True)
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to update draft: {str(e)}")


@router.delete("/drafts/{draft_id}", tags=["Drafts"])
async def delete_draft(
    draft_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Delete a draft."""
    try:
        draft = await reddit.drafts(draft_id)
        await draft.delete()
        return {"message": "Draft deleted successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to delete draft: {str(e)}")


@router.post("/drafts/{draft_id}/submit", response_model=SubmissionInfo, tags=["Drafts"])
async def submit_draft(
    draft_id: str,
    title: Optional[str] = None,
    selftext: Optional[str] = None,
    url: Optional[str] = None,
    subreddit: Optional[str] = None,
    flair_id: Optional[str] = None,
    flair_text: Optional[str] = None,
    nsfw: Optional[bool] = None,
    spoiler: Optional[bool] = None,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Submit a draft as a post."""
    try:
        draft = await reddit.drafts(draft_id)

        # Prepare submission kwargs
        submit_kwargs = {}
        if title is not None:
            submit_kwargs['title'] = title
        if selftext is not None:
            submit_kwargs['selftext'] = selftext
        if url is not None:
            submit_kwargs['url'] = url
        if subreddit is not None:
            submit_kwargs['subreddit'] = subreddit
        if flair_id is not None:
            submit_kwargs['flair_id'] = flair_id
        if flair_text is not None:
            submit_kwargs['flair_text'] = flair_text
        if nsfw is not None:
            submit_kwargs['nsfw'] = nsfw
        if spoiler is not None:
            submit_kwargs['spoiler'] = spoiler

        submission = await draft.submit(**submit_kwargs)
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
        raise RedditAPIException(f"Failed to submit draft: {str(e)}")