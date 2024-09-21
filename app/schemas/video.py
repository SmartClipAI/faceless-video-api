from pydantic import BaseModel

class VideoRequest(BaseModel):
    story_topic: str
    image_style: str
    duration: int
    language: str
    voice_name: str

class VideoResponse(BaseModel):
    task_id: str
    status: str

class TaskStatus(BaseModel):
    status: str
    progress: float