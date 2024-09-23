from fastapi import FastAPI
from app.api.endpoints import video, image, auth
from app.core.config import settings
from app.core.logging import setup_logging

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(video.router, prefix="/v1", tags=["video"])
app.include_router(image.router, prefix="/v1", tags=["image"])