from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ImageRequest(BaseModel):
    story_topic: str
    art_style: str

class ImageResponse(BaseModel):
    task_id: str
    status: str

class RegenerateImageResponse(BaseModel):
    task_id: str
    urls: List[str]
    status: str
    created_at: datetime
    updated_at: datetime

class ImageStatus(BaseModel):
    id: str
    status: str
    urls: Optional[List[str]] = None
    subtitles: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None  # Make updated_at optional

class ImageTaskStatus(BaseModel):
    task_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    story_text: Optional[str]
    images: List[ImageStatus]
