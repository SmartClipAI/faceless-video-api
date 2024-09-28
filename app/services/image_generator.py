import re
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from app.services.image_api import fal_flux_api, replicate_flux_api
from app.core.config import settings
from app.core.logging import logger
from app.utils.helpers import create_blank_image
from app.models.image import Image
from app.models.image_task import ImageTask
import asyncio
import time

class ImageGenerator:
    def __init__(self, image_generator_func: Callable[[str], Optional[str]] = None):
        self.image_generator_func = image_generator_func 

    async def prepare_and_generate_image(
        self,
        task_id: str,
        storyboard: Dict[str, Any],
        characters: List[Dict[str, Any]],
        style: str
    ) -> Optional[str]:
        # Construct the prompt
        prompt = storyboard['description']
        camera_info = f"Camera: {storyboard['camera']['angle']}, {storyboard['camera']['composition_type']}, {storyboard['camera']['shot_size']}"
        lighting_info = f"Lighting: {storyboard['lighting']}"
        
        enhanced_prompt = f"{prompt} | {style} | {camera_info} | {lighting_info}"
        
        # Add character descriptions
        character_descriptions = []
      
        for character in characters:
            name_forms = [
                character['name'].split()[0],  # First name
                character['name'],  # Full name
                f"{character['name'].split()[0]}'s",  # First name possessive
                f"{character['name']}'s",  # Full name possessive
                f"{character['name'].split()[0]}'",  # First name possessive (alternative)
                f"{character['name']}'"  # Full name possessive (alternative)
            ]
            
            # Check if any non-bracketed form of the name is in the prompt
            if any(
                form.lower() in prompt.lower() and 
                f"{{{{{form.lower()}}}}}" not in prompt.lower()
                for form in name_forms
            ):
                desc = f"{character['name']}'s appearance: {character['ethnicity']} {character['gender']} {character['age']} {character['facial_features']} {character['body_type']} {character['hair_style']} {character['accessories']}"
                character_descriptions.append(desc)

        if character_descriptions:
            enhanced_prompt += " | " + " | ".join(character_descriptions)
        
        # Remove all bracketed content
        enhanced_prompt = re.sub(r'\{\{.*?\}\}', '', enhanced_prompt)
        
        logger.debug(f"Enhanced prompt for task {task_id}: {enhanced_prompt}")

        image_url = await self.image_generator_func(task_id, enhanced_prompt)
        
        if image_url:
            logger.info(f"Image generated successfully for task {task_id}")
        else:
            logger.error(f"Failed to generate image for task {task_id}")

        return image_url, enhanced_prompt

    async def generate_images(self, task_id: str, storyboard_project: Dict[str, Any], art_style: str) -> List[str]:
        start_time = time.time()
        tasks = []

        characters = storyboard_project.get('characters', [])
        for i, storyboard in enumerate(storyboard_project['storyboards']):
            task = self.prepare_and_generate_image(task_id, storyboard, characters, art_style)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        image_urls = []
        for i, result in enumerate(results):
            if isinstance(result, tuple) and len(result) == 2:
                image_url, enhanced_prompt = result
                if image_url is not None:
                    storyboard_project['storyboards'][i]['image'] = image_url
                    storyboard_project['storyboards'][i]['enhanced_prompt'] = enhanced_prompt
                    storyboard_project['storyboards'][i]['error_message'] = None
                    image_urls.append(image_url)
                    logger.info(f"Image {i+1} generated successfully for task {task_id}: {image_url}")
                else:
                    error_message = "Image generation failed: image_url is None"
                    logger.error(f"Error generating image {i+1} for task {task_id}: {error_message}")
                    storyboard_project['storyboards'][i]['image'] = None
                    storyboard_project['storyboards'][i]['enhanced_prompt'] = enhanced_prompt
                    storyboard_project['storyboards'][i]['error_message'] = error_message
                    image_urls.append(None)
            else:
                if isinstance(result, Exception):
                    error_message = str(result)
                else:
                    error_message = f"Unexpected result: {result}"
                
                logger.error(f"Error generating image {i+1} for task {task_id}: {error_message}")
                storyboard_project['storyboards'][i]['image'] = None
                storyboard_project['storyboards'][i]['enhanced_prompt'] = None
                storyboard_project['storyboards'][i]['error_message'] = error_message
                image_urls.append(None)

        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"generate_images completed for task {task_id} in {total_time:.2f} seconds")
        logger.info(f"Total images generated for task {task_id}: {len(image_urls)}")

        return image_urls

    async def regenerate_image(self, task_id: str, image_id: str) -> Optional[str]:
        # Get the original image
        image = await Image.get(image_id)
        if not image:
            logger.error(f"Image not found: {image_id}")
            return None

        # Generate a new image using the prompt
        image_url = await self.image_generator_func(task_id, image.enhanced_prompt)

        current_time = datetime.now()

        if image_url:
            # Update the image with the new URL and status
            await Image.update(image_id, url=image_url, status="completed", updated_at=current_time)
            logger.info(f"Image regenerated successfully for task {task_id}, image {image_id}")
        else:
            # Update the image status to failed if generation was unsuccessful
            await Image.update(image_id, status="failed", updated_at=current_time)
            logger.error(f"Failed to regenerate image for task {task_id}, image {image_id}")

        # Update the image_task's updated_at field
        await ImageTask.update(task_id, updated_at=current_time)

        return image_url