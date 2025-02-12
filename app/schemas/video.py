from pydantic import BaseModel, field_validator
from typing import List, Optional, Literal
from datetime import datetime
from .image import ImageStatus
from app.constants.story_types import STORY_TYPES

ArtStyle = Literal['photorealistic', 'cinematic', 'anime', 'comic-book', 'pixar-art']
Duration = Literal['short', 'long']
Language = Literal['english', 'czech', 'danish', 'dutch', 'french', 'german', 'greek', 'hindi', 'indonesian', 'italian', 'chinese', 'japanese', 'norwegian', 'polish', 'portuguese', 'russian', 'spanish', 'swedish', 'turkish', 'ukrainian']
VoiceName = Literal['echo', 'alloy', 'onyx', 'fable', 'nova', 'shimmer']
Status = Literal['queued', 'processing', 'completed', 'failed']
StoryTopic = Literal[tuple(STORY_TYPES)]  # Create Literal type from STORY_TYPES

class VideoRequest(BaseModel):
    story_topic: StoryTopic
    art_style: ArtStyle
    duration: Duration
    language: Language
    voice_name: VoiceName

    @field_validator('story_topic', 'art_style', 'duration', 'language', 'voice_name', mode='before')
    def to_lowercase(cls, v):
        return v.lower() if isinstance(v, str) else v

class VideoResponse(BaseModel):
    task_id: str
    status: Status

class VideoTaskStatus(BaseModel):
    task_id: str
    status: Status
    progress: float
    url: Optional[str] = None
    story_title: Optional[str] = None
    story_description: Optional[str] = None
    story_text: Optional[str] = None
    images: List[ImageStatus]
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

