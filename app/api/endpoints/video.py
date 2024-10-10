from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.schemas.video import VideoRequest, VideoResponse, VideoTaskStatus
from app.core.security import get_current_user
from app.models.video_task import VideoTask
from app.services.video_task_processor import VideoTaskProcessor
from uuid import uuid4
from app.models.image import Image
from app.schemas.image import ImageStatus

router = APIRouter()
video_task_processor = VideoTaskProcessor()

@router.post("/generate", response_model=VideoResponse)
async def generate_video(
    request: VideoRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    task_id = str(uuid4())
    await VideoTask.create(id=task_id, status="queued", progress=0.0, story_topic=request.story_topic, art_style=request.art_style, duration=request.duration, language=request.language, voice_name=request.voice_name)
    background_tasks.add_task(video_task_processor.process_video_generation_task, task_id, request.story_topic, request.art_style, request.duration, request.language, request.voice_name)
    return VideoResponse(task_id=task_id, status="queued")

@router.get("/status/tasks/{task_id}", response_model=VideoTaskStatus)
async def get_task_status(task_id: str, current_user: dict = Depends(get_current_user)):
    task = await VideoTask.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    images = await Image.list_by_task(task_id)
    return VideoTaskStatus(
        task_id=task.id,
        status=task.status,
        progress=task.progress,
        url=task.url,
        story_title=task.story_title,
        story_description=task.story_description,
        story_text=task.story_text,
        created_at=task.created_at,
        updated_at=task.updated_at,
        images=[ImageStatus(
            id=image.id,
            status=image.status,
            urls=image.urls,
            subtitles=image.subtitles,
            created_at=image.created_at,
            updated_at=image.updated_at
        ) for image in images]
    )
