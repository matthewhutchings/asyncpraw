"""
Refresh and data loading endpoints for Reddit API wrapper.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
import asyncpraw

from models import CommentInfo, SubmissionInfo
from auth import get_reddit_client
from exceptions import RedditAPIException

router = APIRouter()


@router.post("/comment/{comment_id}/refresh", response_model=CommentInfo, tags=["Data Refresh"])
async def refresh_comment(
    comment_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Refresh a comment to get updated data and replies."""
    try:
        comment = await reddit.comment(comment_id)
        await comment.refresh()

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
        raise RedditAPIException(f"Failed to refresh comment: {str(e)}")


@router.post("/submission/{submission_id}/refresh", response_model=SubmissionInfo, tags=["Data Refresh"])
async def refresh_submission(
    submission_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Refresh a submission to get updated data."""
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
        raise RedditAPIException(f"Failed to refresh submission: {str(e)}")


@router.get("/comment/{comment_id}/replies", response_model=List[CommentInfo], tags=["Data Refresh"])
async def get_comment_replies(
    comment_id: str,
    sort: str = Query("best", regex="^(best|top|new|controversial|old|qa)$"),
    limit: Optional[int] = Query(None, ge=1, le=500),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get replies to a comment with optional sorting and limit."""
    try:
        comment = await reddit.comment(comment_id)

        # Set reply sort if specified
        if hasattr(comment, 'reply_sort'):
            comment.reply_sort = sort
        if limit and hasattr(comment, 'reply_limit'):
            comment.reply_limit = limit

        await comment.refresh()

        replies = []
        for reply in comment.replies:
            if hasattr(reply, 'body'):  # Skip MoreComments objects
                replies.append(CommentInfo(
                    id=reply.id,
                    author=reply.author.name if reply.author else "[deleted]",
                    body=reply.body,
                    score=reply.score,
                    created_utc=reply.created_utc,
                    permalink=f"https://reddit.com{reply.permalink}",
                    is_submitter=reply.is_submitter,
                    parent_id=reply.parent_id,
                    submission_id=reply.submission.id
                ))

        return replies
    except Exception as e:
        raise RedditAPIException(f"Failed to get comment replies: {str(e)}")


@router.post("/submission/{submission_id}/load_comments", response_model=List[CommentInfo], tags=["Data Refresh"])
async def load_submission_comments(
    submission_id: str,
    sort: str = Query("best", regex="^(best|top|new|controversial|old|qa)$"),
    limit: Optional[int] = Query(None, ge=1, le=500),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Load comments for a submission with optional sorting and limit."""
    try:
        submission = await reddit.submission(submission_id)
        submission.comment_sort = sort
        if limit:
            submission.comment_limit = limit

        await submission.load()

        comments = []
        for comment in submission.comments.list():
            if hasattr(comment, 'body'):  # Skip MoreComments objects
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
        raise RedditAPIException(f"Failed to load submission comments: {str(e)}")


@router.post("/submission/{submission_id}/replace_more_comments", tags=["Data Refresh"])
async def replace_more_comments(
    submission_id: str,
    limit: int = Query(32, ge=0, le=100),
    threshold: int = Query(0, ge=0),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Replace MoreComments objects with actual comments."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.load()

        replaced = await submission.comments.replace_more(limit=limit, threshold=threshold)

        return {
            "message": "MoreComments replaced successfully",
            "replaced_count": len(replaced),
            "total_comments": len(submission.comments.list())
        }
    except Exception as e:
        raise RedditAPIException(f"Failed to replace more comments: {str(e)}")


@router.get("/comment/{comment_id}/parent", response_model=CommentInfo, tags=["Data Refresh"])
async def get_comment_parent(
    comment_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get the parent comment of a comment."""
    try:
        comment = await reddit.comment(comment_id)
        parent = await comment.parent()

        if hasattr(parent, 'body'):  # It's a comment
            return CommentInfo(
                id=parent.id,
                author=parent.author.name if parent.author else "[deleted]",
                body=parent.body,
                score=parent.score,
                created_utc=parent.created_utc,
                permalink=f"https://reddit.com{parent.permalink}",
                is_submitter=parent.is_submitter,
                parent_id=parent.parent_id,
                submission_id=parent.submission.id
            )
        else:  # It's a submission (parent comment)
            raise HTTPException(status_code=404, detail="Parent is a submission, not a comment")

    except Exception as e:
        raise RedditAPIException(f"Failed to get comment parent: {str(e)}")


@router.get("/comment/{comment_id}/context", response_model=List[CommentInfo], tags=["Data Refresh"])
async def get_comment_context(
    comment_id: str,
    context: int = Query(8, ge=1, le=10),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get comment with context (parent comments)."""
    try:
        comment = await reddit.comment(comment_id)

        # Set context and refresh
        if hasattr(comment, 'context'):
            comment.context = context
        await comment.refresh()

        # Get the submission and find the comment thread
        submission = comment.submission
        await submission.load()

        # Find the comment and its context in the submission
        context_comments = []

        def find_comment_thread(comment_list, target_id):
            for c in comment_list:
                if hasattr(c, 'id') and c.id == target_id:
                    return [c]
                if hasattr(c, 'replies'):
                    result = find_comment_thread(c.replies, target_id)
                    if result:
                        return [c] + result
            return []

        thread = find_comment_thread(submission.comments, comment_id)

        for c in thread:
            if hasattr(c, 'body'):
                context_comments.append(CommentInfo(
                    id=c.id,
                    author=c.author.name if c.author else "[deleted]",
                    body=c.body,
                    score=c.score,
                    created_utc=c.created_utc,
                    permalink=f"https://reddit.com{c.permalink}",
                    is_submitter=c.is_submitter,
                    parent_id=c.parent_id,
                    submission_id=c.submission.id
                ))

        return context_comments
    except Exception as e:
        raise RedditAPIException(f"Failed to get comment context: {str(e)}")


@router.get("/submission/{submission_id}/comment_forest", response_model=Dict[str, Any], tags=["Data Refresh"])
async def get_comment_forest_info(
    submission_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get information about the comment forest structure."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.load()

        total_comments = len(submission.comments.list())

        # Count MoreComments objects
        more_comments_count = 0
        for item in submission.comments:
            if hasattr(item, 'count'):  # MoreComments object
                more_comments_count += item.count

        return {
            "total_comments_loaded": total_comments,
            "more_comments_available": more_comments_count,
            "submission_comment_count": submission.num_comments,
            "forest_size": len(submission.comments)
        }
    except Exception as e:
        raise RedditAPIException(f"Failed to get comment forest info: {str(e)}")