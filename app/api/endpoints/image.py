from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from app.schemas.image import ImageRequest, ImageResponse, ImageTaskStatus, ImageStatus, RegenerateImageResponse
from app.core.security import get_current_user
from app.core.config import settings
from app.models.image_task import ImageTask
from app.models.image import Image
from app.services.image_generator import ImageGenerator
from app.services.image_task_processor import ImageTaskProcessor
from app.services.image_api import fal_flux_api, replicate_flux_api
from uuid import uuid4

router = APIRouter()
image_gen_func = fal_flux_api if settings.use_fal_flux else replicate_flux_api
image_generator = ImageGenerator(image_generator_func=image_gen_func)
image_task_processor = ImageTaskProcessor()

@router.post("/images", response_model=ImageResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_story_images(
    request: ImageRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    task_id = str(uuid4())
    await ImageTask.create(id=task_id, status="queued", progress=0.0, story_topic=request.story_topic, art_style=request.art_style)
    background_tasks.add_task(image_task_processor.process_image_generation_task, task_id, request.story_topic, request.art_style)
    return ImageResponse(task_id=task_id, status="queued")

@router.get("/images/tasks/{task_id}", response_model=ImageTaskStatus)
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
            subtitles=image.subtitles,
            created_at=image.created_at,
            updated_at=image.updated_at if image.updated_at else None
        ) for image in images]
    )

@router.post("/images/{image_id}", response_model=RegenerateImageResponse, status_code=status.HTTP_200_OK)
async def regenerate_image(
    image_id: str,
    current_user: dict = Depends(get_current_user)
):
    image = await Image.get(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    new_image_url = await image_generator.regenerate_image(image.task_id, image_id)
    
    if new_image_url:
        updated_image = await Image.get(image_id)
        return RegenerateImageResponse(
            task_id=image.task_id,
            status=updated_image.status,
            url=new_image_url,
            created_at=updated_image.created_at,
            updated_at=updated_image.updated_at
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to regenerate image")


# @router.get("/images/{image_id}", response_model=ImageStatus)
# async def get_image_status(image_id: str, current_user: dict = Depends(get_current_user)):
#     image = await Image.get(image_id)
#     if not image:
#         raise HTTPException(status_code=404, detail="Image not found")
    
#     return ImageStatus(
#         id=image.id,
#         status=image.status,
#         url=image.url,
#         subtitles=image.subtitles,
#         created_at=image.created_at,
#         updated_at=image.updated_at
#     )