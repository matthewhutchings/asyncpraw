"""
Additional API endpoints for extended Reddit functionality.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import asyncpraw

from models import SubmissionInfo, CommentInfo, UserInfo
from auth import get_reddit_client
from exceptions import RedditAPIException

router = APIRouter()


@router.post("/comment/{comment_id}/reply", response_model=CommentInfo, tags=["Comments"])
async def reply_to_comment(
    comment_id: str,
    body: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Reply to a specific comment."""
    try:
        comment = await reddit.comment(comment_id)
        reply = await comment.reply(body)
        await reply.load()

        return CommentInfo(
            id=reply.id,
            author=reply.author.name if reply.author else "[deleted]",
            body=reply.body,
            score=reply.score,
            created_utc=reply.created_utc,
            permalink=f"https://reddit.com{reply.permalink}",
            is_submitter=reply.is_submitter,
            parent_id=reply.parent_id,
            submission_id=reply.submission.id
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to reply to comment: {str(e)}")


@router.post("/submission/{submission_id}/upvote", tags=["Voting"])
async def upvote_submission(
    submission_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Upvote a submission."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.upvote()
        return {"message": "Submission upvoted successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to upvote submission: {str(e)}")


@router.post("/submission/{submission_id}/downvote", tags=["Voting"])
async def downvote_submission(
    submission_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Downvote a submission."""
    try:
        submission = await reddit.submission(submission_id)
        await submission.downvote()
        return {"message": "Submission downvoted successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to downvote submission: {str(e)}")


@router.post("/comment/{comment_id}/upvote", tags=["Voting"])
async def upvote_comment(
    comment_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Upvote a comment."""
    try:
        comment = await reddit.comment(comment_id)
        await comment.upvote()
        return {"message": "Comment upvoted successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to upvote comment: {str(e)}")


@router.post("/comment/{comment_id}/downvote", tags=["Voting"])
async def downvote_comment(
    comment_id: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Downvote a comment."""
    try:
        comment = await reddit.comment(comment_id)
        await comment.downvote()
        return {"message": "Comment downvoted successfully"}
    except Exception as e:
        raise RedditAPIException(f"Failed to downvote comment: {str(e)}")


@router.get("/subreddit/{subreddit_name}/top", response_model=List[SubmissionInfo], tags=["Subreddits"])
async def get_subreddit_top(
    subreddit_name: str,
    time_filter: str = Query("day", regex="^(hour|day|week|month|year|all)$"),
    limit: int = Query(25, ge=1, le=100),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get top submissions from a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        submissions = []

        async for submission in subreddit.top(time_filter=time_filter, limit=limit):
            submissions.append(SubmissionInfo(
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
            ))

        return submissions
    except Exception as e:
        raise RedditAPIException(f"Failed to get top submissions: {str(e)}")


@router.get("/user/me", response_model=UserInfo, tags=["User"])
async def get_current_user(
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get information about the authenticated user."""
    try:
        user = await reddit.user.me()
        await user.load()

        return UserInfo(
            name=user.name,
            created_utc=user.created_utc,
            comment_karma=user.comment_karma,
            link_karma=user.link_karma,
            is_gold=user.is_gold,
            is_mod=user.is_mod,
            has_verified_email=user.has_verified_email
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to get current user info: {str(e)}")


@router.get("/user/me/submissions", response_model=List[SubmissionInfo], tags=["User"])
async def get_my_submissions(
    limit: int = Query(25, ge=1, le=100),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get submissions by the authenticated user."""
    try:
        user = await reddit.user.me()
        submissions = []

        async for submission in user.submissions.new(limit=limit):
            submissions.append(SubmissionInfo(
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
            ))

        return submissions
    except Exception as e:
        raise RedditAPIException(f"Failed to get user submissions: {str(e)}")


@router.get("/user/me/comments", response_model=List[CommentInfo], tags=["User"])
async def get_my_comments(
    limit: int = Query(25, ge=1, le=100),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get comments by the authenticated user."""
    try:
        user = await reddit.user.me()
        comments = []

        async for comment in user.comments.new(limit=limit):
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
        raise RedditAPIException(f"Failed to get user comments: {str(e)}")


@router.get("/subreddit/{subreddit_name}/moderators", response_model=List[UserInfo], tags=["Moderation"])
async def get_subreddit_moderators(
    subreddit_name: str,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get moderators of a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        moderators = []

        async for moderator in subreddit.moderator():
            moderator_info = await reddit.redditor(moderator.name)
            await moderator_info.load()

            moderators.append(UserInfo(
                name=moderator_info.name,
                created_utc=moderator_info.created_utc,
                comment_karma=moderator_info.comment_karma,
                link_karma=moderator_info.link_karma,
                is_gold=moderator_info.is_gold,
                is_mod=moderator_info.is_mod,
                has_verified_email=moderator_info.has_verified_email
            ))

        return moderators
    except Exception as e:
        raise RedditAPIException(f"Failed to get subreddit moderators: {str(e)}")