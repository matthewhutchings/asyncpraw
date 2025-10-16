"""
Advanced submission features for Reddit API wrapper.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
import asyncpraw

from models import SubmissionInfo, PollSubmissionCreate, GallerySubmissionCreate
from auth import get_reddit_client
from exceptions import RedditAPIException

router = APIRouter()


@router.post("/subreddit/{subreddit_name}/submit_poll", response_model=SubmissionInfo, tags=["Advanced Submissions"])
async def submit_poll(
    subreddit_name: str,
    poll_data: PollSubmissionCreate,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Submit a poll to a subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        submission = await subreddit.submit_poll(
            title=poll_data.title,
            selftext=poll_data.selftext,
            options=poll_data.options,
            duration=poll_data.duration,
            flair_id=poll_data.flair_id,
            flair_text=poll_data.flair_text,
            nsfw=poll_data.nsfw,
            spoiler=poll_data.spoiler,
            send_replies=poll_data.send_replies
        )
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
        raise RedditAPIException(f"Failed to submit poll: {str(e)}")


@router.post("/subreddit/{subreddit_name}/submit_image", response_model=SubmissionInfo, tags=["Advanced Submissions"])
async def submit_image(
    subreddit_name: str,
    title: str = Form(...),
    image: UploadFile = File(...),
    selftext: Optional[str] = Form(""),
    flair_id: Optional[str] = Form(None),
    flair_text: Optional[str] = Form(None),
    nsfw: bool = Form(False),
    spoiler: bool = Form(False),
    send_replies: bool = Form(True),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Submit an image to a subreddit."""
    try:
        # Save uploaded file temporarily
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.filename)[1]) as tmp_file:
            content = await image.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            subreddit = await reddit.subreddit(subreddit_name)
            submission = await subreddit.submit_image(
                title=title,
                image_path=tmp_file_path,
                selftext=selftext,
                flair_id=flair_id,
                flair_text=flair_text,
                nsfw=nsfw,
                spoiler=spoiler,
                send_replies=send_replies
            )

            if submission:
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
            else:
                raise RedditAPIException("Image submission failed - no submission returned")

        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)

    except Exception as e:
        raise RedditAPIException(f"Failed to submit image: {str(e)}")


@router.post("/subreddit/{subreddit_name}/submit_gallery", response_model=SubmissionInfo, tags=["Advanced Submissions"])
async def submit_gallery(
    subreddit_name: str,
    title: str = Form(...),
    images: List[UploadFile] = File(...),
    captions: Optional[List[str]] = Form(None),
    flair_id: Optional[str] = Form(None),
    flair_text: Optional[str] = Form(None),
    nsfw: bool = Form(False),
    spoiler: bool = Form(False),
    send_replies: bool = Form(True),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Submit a gallery to a subreddit."""
    try:
        import tempfile
        import os

        # Process uploaded images
        image_data = []
        temp_files = []

        for i, image in enumerate(images):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.filename)[1]) as tmp_file:
                content = await image.read()
                tmp_file.write(content)
                temp_files.append(tmp_file.name)

                caption = captions[i] if captions and i < len(captions) else ""
                image_data.append({
                    "image_path": tmp_file.name,
                    "caption": caption
                })

        try:
            subreddit = await reddit.subreddit(subreddit_name)
            submission = await subreddit.submit_gallery(
                title=title,
                images=image_data,
                flair_id=flair_id,
                flair_text=flair_text,
                nsfw=nsfw,
                spoiler=spoiler,
                send_replies=send_replies
            )
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

        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                os.unlink(temp_file)

    except Exception as e:
        raise RedditAPIException(f"Failed to submit gallery: {str(e)}")


@router.post("/subreddit/{subreddit_name}/submit_video", response_model=SubmissionInfo, tags=["Advanced Submissions"])
async def submit_video(
    subreddit_name: str,
    title: str = Form(...),
    video: UploadFile = File(...),
    thumbnail: Optional[UploadFile] = File(None),
    selftext: Optional[str] = Form(""),
    flair_id: Optional[str] = Form(None),
    flair_text: Optional[str] = Form(None),
    nsfw: bool = Form(False),
    spoiler: bool = Form(False),
    send_replies: bool = Form(True),
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Submit a video to a subreddit."""
    try:
        import tempfile
        import os

        # Save video file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video.filename)[1]) as tmp_video:
            video_content = await video.read()
            tmp_video.write(video_content)
            video_path = tmp_video.name

        thumbnail_path = None
        if thumbnail:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(thumbnail.filename)[1]) as tmp_thumb:
                thumb_content = await thumbnail.read()
                tmp_thumb.write(thumb_content)
                thumbnail_path = tmp_thumb.name

        try:
            subreddit = await reddit.subreddit(subreddit_name)
            submission = await subreddit.submit_video(
                title=title,
                video_path=video_path,
                thumbnail_path=thumbnail_path,
                selftext=selftext,
                flair_id=flair_id,
                flair_text=flair_text,
                nsfw=nsfw,
                spoiler=spoiler,
                send_replies=send_replies
            )

            if submission:
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
            else:
                raise RedditAPIException("Video submission failed - no submission returned")

        finally:
            # Clean up temporary files
            os.unlink(video_path)
            if thumbnail_path:
                os.unlink(thumbnail_path)

    except Exception as e:
        raise RedditAPIException(f"Failed to submit video: {str(e)}")


@router.post("/submission/{submission_id}/crosspost", response_model=SubmissionInfo, tags=["Advanced Submissions"])
async def crosspost_submission(
    submission_id: str,
    subreddit_name: str,
    title: Optional[str] = None,
    flair_id: Optional[str] = None,
    flair_text: Optional[str] = None,
    nsfw: bool = False,
    spoiler: bool = False,
    send_replies: bool = True,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Crosspost a submission to another subreddit."""
    try:
        submission = await reddit.submission(submission_id)
        target_subreddit = await reddit.subreddit(subreddit_name)

        crosspost = await submission.crosspost(
            subreddit=target_subreddit,
            title=title,
            flair_id=flair_id,
            flair_text=flair_text,
            nsfw=nsfw,
            spoiler=spoiler,
            send_replies=send_replies
        )
        await crosspost.load()

        return SubmissionInfo(
            id=crosspost.id,
            title=crosspost.title,
            author=crosspost.author.name if crosspost.author else "[deleted]",
            score=crosspost.score,
            url=crosspost.url,
            permalink=f"https://reddit.com{crosspost.permalink}",
            created_utc=crosspost.created_utc,
            num_comments=crosspost.num_comments,
            selftext=crosspost.selftext,
            is_self=crosspost.is_self,
            over_18=crosspost.over_18,
            subreddit=crosspost.subreddit.display_name
        )
    except Exception as e:
        raise RedditAPIException(f"Failed to crosspost submission: {str(e)}")


@router.get("/submission/{submission_id}/duplicates", response_model=List[SubmissionInfo], tags=["Advanced Submissions"])
async def get_submission_duplicates(
    submission_id: str,
    limit: int = 25,
    reddit: asyncpraw.Reddit = Depends(get_reddit_client)
):
    """Get duplicate submissions."""
    try:
        submission = await reddit.submission(submission_id)
        duplicates = []

        async for duplicate in submission.duplicates(limit=limit):
            duplicates.append(SubmissionInfo(
                id=duplicate.id,
                title=duplicate.title,
                author=duplicate.author.name if duplicate.author else "[deleted]",
                score=duplicate.score,
                url=duplicate.url,
                permalink=f"https://reddit.com{duplicate.permalink}",
                created_utc=duplicate.created_utc,
                num_comments=duplicate.num_comments,
                selftext=duplicate.selftext,
                is_self=duplicate.is_self,
                over_18=duplicate.over_18,
                subreddit=duplicate.subreddit.display_name
            ))

        return duplicates
    except Exception as e:
        raise RedditAPIException(f"Failed to get duplicates: {str(e)}")