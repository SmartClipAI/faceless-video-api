import os
import re
from typing import Optional, Dict, Any, List, Callable
from app.services.image_api import fal_flux_api, replicate_flux_api
from app.core.config import settings
from app.core.logging import logger
from app.utils.helpers import create_blank_image
import asyncio
import time

class ImageGenerator:
    def __init__(self, image_generator_func: Callable[[str], Optional[bytes]] = None):
        self.image_generator_func = image_generator_func 

    async def generate_image(
        self,
        storyboard: Dict[str, Any],
        characters: List[Dict[str, Any]],
        style: str
    ) -> Optional[bytes]:
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
        
        for character in character_descriptions:
            logger.debug(f"Character description: {character}")

        logger.debug(f"Enhanced prompt: {enhanced_prompt}")

        return await self.image_generator_func(enhanced_prompt)

    async def generate_and_download_images(
        self,
        task_id: str,
        storyboard_project: Dict[str, Any],
        story_dir: str,
        image_style: str
    ) -> List[str]:
        start_time = time.time()
        image_files = []
        tasks = []

        try:
            for i, storyboard in enumerate(storyboard_project['storyboards']):
                image_filename = os.path.join(story_dir, f"image_{i+1}.png")
                prompt = f"{image_style}. {storyboard['description']}"
                
                task = asyncio.create_task(self.generate_single_image(task_id, prompt, image_filename, storyboard, i+1))
                tasks.append(task)

            # wait for all tasks to complete
            results = await asyncio.gather(*tasks)

            for result, storyboard in zip(results, storyboard_project['storyboards']):
                if result:
                    image_filename, success = result
                    if success:
                        storyboard['image'] = image_filename
                        image_files.append(image_filename)
                    else:
                        # TODO: use a placeholder image
                        create_blank_image(image_filename)
                        storyboard['image'] = image_filename
                        image_files.append(image_filename)

        except Exception as e:
            logger.error(f"Error in generate_and_download_images: {e}")

        finally:
            end_time = time.time()
            total_time = end_time - start_time
            logger.info(f"generate_and_download_images completed in {total_time:.2f} seconds")
            logger.info(f"Total images generated: {len(image_files)}")

        return image_files

    async def generate_single_image(self, task_id: str, prompt: str, image_filename: str, storyboard: Dict[str, Any], image_number: int):
        try:
            image_data = await self.image_generator_func(task_id, prompt)
            if image_data:
                with open(image_filename, "wb") as f:
                    f.write(image_data)
                logger.info(f"Image {image_number} generated successfully: {image_filename}")
                return image_filename, True
            else:
                logger.warning(f"Failed to generate image {image_number}")
                return image_filename, False
        except Exception as e:
            logger.error(f"Error generating image {image_number}: {e}")
            return image_filename, False
