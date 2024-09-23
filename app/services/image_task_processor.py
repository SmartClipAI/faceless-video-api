from uuid import uuid4
from openai import AsyncAzureOpenAI
from app.models.image_task import ImageTask
from app.models.image import Image
from app.core.config import settings
from app.utils.helpers import create_resource_dir
from app.services.story_generator import StoryGenerator
from app.services.image_generator import ImageGenerator
from app.constants.story_types import STORY_TYPES
from app.services.image_api import huggingface_flux_api, replicate_flux_api

class ImageTaskProcessor:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.azure_api_version
        )
        self.story_generator = StoryGenerator(self.client)
        
        # Choose the image generation function based on configuration
        image_gen_func = huggingface_flux_api if settings.use_huggingface else replicate_flux_api
        self.image_generator = ImageGenerator(image_generator_func=image_gen_func)

    async def process_image_generation_task(self, task_id: str, story_topic: str, art_style: str):
        task = await ImageTask.get(task_id)
        await task.update(task_id=task_id, status="Generating story")

        story_type = self.map_topic_to_story_type(story_topic)
        title, story = await self.story_generator.generate_story_and_title(story_type)
        if not title or not story:
            await task.update(task_id=task_id, status="Failed")
            return

        await task.update(task_id=task_id, progress=0.2)

        story_dir = create_resource_dir(settings.STORY_DIR, story_type, title)

        characters = await self.story_generator.generate_characters(story) if story_type not in ['life pro tips', 'fun facts'] else []
        
        await task.update(task_id=task_id, progress=0.3)

        storyboard_project = await self.story_generator.generate_storyboard(story_type, title, story, [c["name"] for c in characters])
        if not storyboard_project.get("storyboards"):
            await task.update(task_id=task_id, status="Failed")
            return

        await task.update(task_id=task_id, progress=0.5)

        storyboard_project["characters"] = characters

        image_files = await self.image_generator.generate_and_download_images(storyboard_project, story_dir, art_style)

        await task.update(task_id=task_id, progress=0.8)

        if image_files:
            for i, image_file in enumerate(image_files):
                image_url = f"/static/stories/{story_type}/{title}/scene_{i+1}.png"
                await Image.create(
                    id=str(uuid4()),
                    task_id=task_id,
                    url=image_url,
                    subtitles=storyboard_project["storyboards"][i]["description"],
                    status="Completed"
                )
            
            await task.update(task_id=task_id, status="Completed", progress=1.0, story_text=story)
        else:
            await task.update(task_id=task_id, status="Failed")

    def map_topic_to_story_type(self, topic: str) -> str:
        topic_lower = topic.lower()
        
        for story_type in STORY_TYPES:
            if topic_lower == story_type.lower():
                return story_type
            elif topic_lower in story_type.lower():
                return story_type
        
        return None