"""
Content editing and deletion endpoints for Reddit API wrapper.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
import asyncpraw

from models import SubmissionInfo, CommentInfo
from auth import get_reddit_client_with_headers
from exceptions import RedditAPIException

router = APIRouter()


@router.post("/comment/{comment_id}/edit", response_model=CommentInfo, tags=["Comments"])
async def edit_comment(
    comment_id: str,
    body: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Edit a comment."""
    try:
        comment = await reddit.comment(comment_id)
        edited_comment = await comment.edit(body)
        await edited_comment.load()

        return CommentInfo(
            id=edited_comment.id,
            author=edited_comment.author.name if edited_comment.author else "[deleted]",
            body=edited_comment.body,
            score=edited_comment.score,
            created_utc=edited_comment.created_utc,
            permalink=f"https://reddit.com{edited_comment.permalink}",
            is_submitter=edited_comment.is_submitter,
            parent_id=edited_comment.parent_id,
            submission_id=edited_comment.submission.id
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to edit comment: {str(e)}")


@router.post("/submission/{submission_id}/edit", response_model=SubmissionInfo, tags=["Submissions"])
async def edit_submission(
    submission_id: str,
    selftext: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Edit a submission's selftext."""
    try:
        submission = await reddit.submission(submission_id)
        edited_submission = await submission.edit(selftext)
        await edited_submission.load()

        return SubmissionInfo(
            id=edited_submission.id,
            title=edited_submission.title,
            author=edited_submission.author.name if edited_submission.author else "[deleted]",
            score=edited_submission.score,
            url=edited_submission.url,
            permalink=f"https://reddit.com{edited_submission.permalink}",
            created_utc=edited_submission.created_utc,
            num_comments=edited_submission.num_comments,
            selftext=edited_submission.selftext,
            is_self=edited_submission.is_self,
            over_18=edited_submission.over_18,
            subreddit=edited_submission.subreddit.display_name
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to edit submission: {str(e)}")


@router.delete("/comment/{comment_id}", tags=["Comments"])
async def delete_comment(
    comment_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Delete a comment."""
    try:
        comment = await reddit.comment(comment_id)
        await comment.delete()
        return {"message": "Comment deleted successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to delete comment: {str(e)}")


@router.delete("/submission/{submission_id}", tags=["Submissions"])
async def delete_submission(
    submission_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Delete a submission."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.delete()
        return {"message": "Submission deleted successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to delete submission: {str(e)}")


@router.post("/comment/{comment_id}/save", tags=["Saved Content"])
async def save_comment(
    comment_id: str,
    category: Optional[str] = None,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Save a comment."""
    try:
        comment = await reddit.comment(comment_id)
        await comment.save(category=category)
        return {"message": "Comment saved successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to save comment: {str(e)}")


@router.post("/submission/{submission_id}/save", tags=["Saved Content"])
async def save_submission(
    submission_id: str,
    category: Optional[str] = None,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Save a submission."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.save(category=category)
        return {"message": "Submission saved successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to save submission: {str(e)}")


@router.post("/comment/{comment_id}/unsave", tags=["Saved Content"])
async def unsave_comment(
    comment_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Unsave a comment."""
    try:
        comment = await reddit.comment(comment_id)
        await comment.unsave()
        return {"message": "Comment unsaved successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to unsave comment: {str(e)}")


@router.post("/submission/{submission_id}/unsave", tags=["Saved Content"])
async def unsave_submission(
    submission_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Unsave a submission."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.unsave()
        return {"message": "Submission unsaved successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to unsave submission: {str(e)}")


@router.get("/user/me/saved", response_model=List[dict], tags=["Saved Content"])
async def get_saved_content(
    limit: int = 25,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Get saved submissions and comments."""
    try:
        saved_items = []
        user = await reddit.user.me()

        async for item in user.saved(limit=limit):
            if hasattr(item, 'title'):  # It's a submission
                saved_items.append({
                    "type": "submission",
                    "data": SubmissionInfo(
                        id=item.id,
                        title=item.title,
                        author=item.author.name if item.author else "[deleted]",
                        score=item.score,
                        url=item.url,
                        permalink=f"https://reddit.com{item.permalink}",
                        created_utc=item.created_utc,
                        num_comments=item.num_comments,
                        selftext=item.selftext,
                        is_self=item.is_self,
                        over_18=item.over_18,
                        subreddit=item.subreddit.display_name
                    )
                })
            else:  # It's a comment
                saved_items.append({
                    "type": "comment",
                    "data": CommentInfo(
                        id=item.id,
                        author=item.author.name if item.author else "[deleted]",
                        body=item.body,
                        score=item.score,
                        created_utc=item.created_utc,
                        permalink=f"https://reddit.com{item.permalink}",
                        is_submitter=item.is_submitter,
                        parent_id=item.parent_id,
                        submission_id=item.submission.id
                    )
                })

        return saved_items
    except Exception as e:
        raise RedditAPIException(f"Failed to get saved content: {str(e)}")


@router.post("/comment/{comment_id}/clear_vote", tags=["Voting"])
async def clear_comment_vote(
    comment_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Clear vote on a comment."""
    try:
        comment = await reddit.comment(comment_id)
        await comment.clear_vote()
        return {"message": "Comment vote cleared successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to clear comment vote: {str(e)}")


@router.post("/submission/{submission_id}/clear_vote", tags=["Voting"])
async def clear_submission_vote(
    submission_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Clear vote on a submission."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.clear_vote()
        return {"message": "Submission vote cleared successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to clear submission vote: {str(e)}")


@router.post("/comment/{comment_id}/report", tags=["Moderation"])
async def report_comment(
    comment_id: str,
    reason: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Report a comment."""
    try:
        comment = await reddit.comment(comment_id)
        await comment.report(reason)
        return {"message": "Comment reported successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to report comment: {str(e)}")


@router.post("/submission/{submission_id}/report", tags=["Moderation"])
async def report_submission(
    submission_id: str,
    reason: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client_with_headers)
):
    """Report a submission."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.report(reason)
        return {"message": "Submission reported successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to report submission: {str(e)}")