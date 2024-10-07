from pydantic import BaseModel

class VideoRequest(BaseModel):
    story_topic: str
    art_style: str
    duration: str
    language: str
    voice_name: str

class VideoResponse(BaseModel):
    task_id: str
    status: str

class TaskStatus(BaseModel):
    status: str
    progress: float