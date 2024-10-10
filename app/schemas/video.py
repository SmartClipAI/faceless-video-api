from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .image import ImageStatus

class VideoRequest(BaseModel):
    story_topic: str
    art_style: str
    duration: str
    language: str
    voice_name: str

class VideoResponse(BaseModel):
    task_id: str
    status: str

class VideoTaskStatus(BaseModel):
    task_id: str
    status: str
    progress: float
    url: Optional[str] = None
    story_title: Optional[str] = None
    story_description: Optional[str] = None
    story_text: Optional[str] = None
    images: List[ImageStatus]
    created_at: datetime
    updated_at: Optional[datetime] = None

