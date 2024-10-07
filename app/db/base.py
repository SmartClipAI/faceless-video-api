# Import base class for SQLAlchemy models
from app.db.base_class import Base

# Import all models
from app.models.user import User
from app.models.image import Image
from app.models.video import Video


# Instead, use this to make sure all models are registered:
from app.models import video_task

# Add any other models here