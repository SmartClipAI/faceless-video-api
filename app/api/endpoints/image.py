from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from app.schemas.image import ImageRequest, ImageResponse, ImageTaskStatus, ImageStatus
from app.core.security import get_current_user
from app.models.image_task import ImageTask
from app.models.image import Image
from app.services.image_generator import ImageGenerator
from uuid import uuid4
from app.services.image_task_processor import ImageTaskProcessor

router = APIRouter()
image_generator = ImageGenerator()
image_task_processor = ImageTaskProcessor()

@router.post("/images", response_model=ImageResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_story_images(
    request: ImageRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    task_id = str(uuid4())
    await ImageTask.create(id=task_id, status="Queued", progress=0.0, story_topic=request.story_topic, art_style=request.art_style)
    background_tasks.add_task(image_task_processor.process_image_generation_task, task_id, request.story_topic, request.art_style)
    return ImageResponse(task_id=task_id, status="Queued")

@router.get("/images/tasks/{task_id}/status", response_model=ImageTaskStatus)
async def get_task_status(task_id: str, current_user: dict = Depends(get_current_user)):
    task = await ImageTask.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    images = await Image.list_by_task(task_id)
    return ImageTaskStatus(
        task_id=task.id,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
        story_text=task.story_text,
        images=[ImageStatus(
            id=image.id,
            status=image.status,
            url=image.url,
            subtitles=image.subtitles
        ) for image in images]
    )

@router.post("/images/{image_id}", response_model=ImageResponse)
async def regenerate_image(
    image_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    image = await Image.get(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    task = await ImageTask.get(image.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    new_task_id = str(uuid4())
    await ImageTask.create(id=new_task_id, status="Queued", progress=0.0, story_topic=task.story_topic, art_style=task.art_style)
    background_tasks.add_task(image_generator.regenerate_image, new_task_id, image_id)
    return ImageResponse(task_id=new_task_id, status="Queued")

@router.get("/images/{image_id}/status", response_model=ImageStatus)
async def get_image_status(image_id: str, current_user: dict = Depends(get_current_user)):
    image = await Image.get(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return ImageStatus(
        id=image.id,
        status=image.status,
        url=image.url,
        subtitles=image.subtitles,
        created_at=image.created_at,
        updated_at=image.updated_at
    )
