# Import base class for SQLAlchemy models
from app.db.base_class import Base

# Import all models
from app.models.user import User
from app.models.video import VideoTask
from app.models.image import Image

# Remove the import of ImageTask from here

# Instead, use this to make sure all models are registered:
from app.models import image_task  # This imports the module, not the class directly

# Add any other models here