import os
from uuid import uuid4
from openai import AsyncAzureOpenAI
from app.core.config import settings
from app.services.story_generator import StoryGenerator
from app.models.image import Image
from app.services.image_generator import ImageGenerator
from app.services.video_creator import VideoCreator
from app.utils.helpers import create_resource_dir
from app.models.video_task import VideoTask
from app.constants.story_types import STORY_TYPES
from app.services.image_api import fal_flux_api, replicate_flux_api
from app.core.logging import logger
from app.utils.image_utils import download_and_save_image

class VideoTaskProcessor:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.azure_api_version
        )
        self.story_generator = StoryGenerator(self.client)

        # Choose the image generation function based on configuration
        image_gen_func = fal_flux_api if settings.use_fal_flux else replicate_flux_api
        self.image_generator = ImageGenerator(image_generator_func=image_gen_func)
        self.video_creator = VideoCreator(self.client)

    async def process_video_generation_task(self, task_id: str, story_topic: str, art_style: str, duration: str, language: str, voice_name: str):
        task = await VideoTask.get(task_id)
        await task.update(task_id=task_id, status="processing")

        story_type = self.map_topic_to_story_type(story_topic)
        title, story = await self.story_generator.generate_story_and_title(story_type, duration)
        if not title or not story:
            logger.error("Failed to generate story and title")
            await task.update(task_id=task_id, status="failed")
            return

        await task.update(task_id=task_id, progress=0.2)

        story_dir = create_resource_dir(settings.STORY_DIR, story_type, title)

        characters = await self.story_generator.generate_characters(story) if story_type not in ['life pro tips', 'fun facts'] else []
        
        await task.update(task_id=task_id, progress=0.3)

        storyboard_project = await self.story_generator.generate_storyboard(story_type, title, story, [c["name"] for c in characters])
        if not storyboard_project.get("storyboards"):
            logger.error("Failed to generate storyboard")
            await task.update(task_id=task_id, status="failed")
            return

        await task.update(task_id=task_id, progress=0.5)

        storyboard_project["characters"] = characters

        # image_files = await self.image_generator.generate_and_download_images(storyboard_project, story_dir, art_style)
        image_urls = await self.image_generator.generate_images(task_id, storyboard_project, art_style)

        await task.update(task_id=task_id, progress=0.8)

        # save images to database and download them
        if image_urls:
            # audio_dir = os.path.join(story_dir, "audio")
            
            for i, image_url in enumerate(image_urls):
                if image_url:
                    # Save image URL to database
                    await Image.create(
                        id=str(uuid4()),
                        task_id=task_id,
                        urls=[image_url],
                        subtitles=storyboard_project["storyboards"][i]["description"],
                        status="completed",
                        enhanced_prompt=storyboard_project["storyboards"][i].get("enhanced_prompt", ""),
                        error_message=storyboard_project["storyboards"][i].get("error_message", "")
                    )
                    
                    # Download and save image file
                    scene_number = storyboard_project["storyboards"][i].get("scene_number", i + 1)
                    image_filename = f"scene_{scene_number}.png"
                    image_path = os.path.join(story_dir, image_filename)
                    
                    success = await download_and_save_image(image_url, image_path)
                    if not success:
                        logger.error(f"Failed to download and save image for scene {scene_number}")
                else:
                    await Image.create(
                        id=str(uuid4()),
                        task_id=task_id,
                        urls=[],
                        subtitles=storyboard_project["storyboards"][i]["description"],
                        status="failed",
                        enhanced_prompt=storyboard_project["storyboards"][i].get("enhanced_prompt", ""),
                        error_message=storyboard_project["storyboards"][i].get("error_message", "")
                    )

            # os.makedirs(audio_dir, exist_ok=True)
            # video_path = os.path.join(story_dir, "story_video.mp4")
            await self.video_creator.create_video(storyboard_project, story_dir, voice_name)
            await task.update(task_id=task_id, status="completed", progress=1.0)
        else:
            await task.update(task_id=task_id, status="failed")

    def map_topic_to_story_type(self, topic: str) -> str:
        topic_lower = topic.lower()
        
        for story_type in STORY_TYPES:
            if topic_lower == story_type.lower():
                return story_type
            elif topic_lower in story_type.lower():
                return story_type
        
        return None