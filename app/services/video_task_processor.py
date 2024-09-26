import os
from openai import AsyncAzureOpenAI
from app.core.config import settings
from app.services.story_generator import StoryGenerator
from app.services.image_generator import ImageGenerator
from app.services.video_creator import VideoCreator
from app.utils.helpers import create_resource_dir
from app.models.video import VideoTask
from app.constants.story_types import STORY_TYPES
from app.services.image_api import fal_flux_api, replicate_flux_api
from app.core.logging import logger

class VideoTaskProcessor:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.azure_api_version
        )
        self.story_generator = StoryGenerator(self.client)
        image_gen_func = fal_flux_api if settings.use_fal_flux else replicate_flux_api
        self.image_generator = ImageGenerator(image_generator_func=image_gen_func)
        self.video_creator = VideoCreator(self.client)

    async def process_video_generation_task(self, task_id: str, story_topic: str, image_style: str, duration: int, language: str, voice_name: str):
        task = await VideoTask.get(task_id)
        await task.update(status="Generating story")

        story_type = self.map_topic_to_story_type(story_topic)
        title, story = await self.story_generator.generate_story_and_title(story_type)
        if not title or not story:
            logger.error("Failed to generate story and title")
            await task.update(status="Failed")
            return

        await task.update(progress=0.2)

        story_dir = create_resource_dir(settings.STORY_DIR, story_type, title)

        characters = await self.story_generator.generate_characters(story) if story_type not in ['life pro tips', 'fun facts'] else []
        
        await task.update(progress=0.3)

        storyboard_project = await self.story_generator.generate_storyboard(story_type, title, story, [c["name"] for c in characters])
        if not storyboard_project.get("storyboards"):
            logger.error("Failed to generate storyboard")
            await task.update(status="Failed")
            return

        await task.update(progress=0.5)

        storyboard_project["characters"] = characters

        image_files = await self.image_generator.generate_and_download_images(storyboard_project, story_dir, image_style)

        await task.update(progress=0.8)

        if image_files:
            audio_dir = os.path.join(story_dir, "audio")
            os.makedirs(audio_dir, exist_ok=True)
            video_path = os.path.join(story_dir, "story_video.mp4")
            await self.video_creator.create_video(storyboard_project, video_path, audio_dir, voice_name)
            
            await task.update(status="Completed", progress=1.0)
        else:
            await task.update(status="Failed")

    def map_topic_to_story_type(self, topic: str) -> str:
        topic_lower = topic.lower()
        
        for story_type in STORY_TYPES:
            if topic_lower == story_type.lower():
                return story_type
            elif topic_lower in story_type.lower():
                return story_type
        
        return None