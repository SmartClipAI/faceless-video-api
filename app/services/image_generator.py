import os
import base64
import requests
import replicate
import re
from typing import Optional, Dict, Any, List, Callable
from app.utils.helpers import create_blank_image
from app.core.config import settings

class ImageGenerator:
    def __init__(self):
        self.replicate_client = replicate.Client(api_token=settings.REPLICATE_API_KEY)

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
            print('---- character ----\n', character)
        
        print('---- prompt ----\n', enhanced_prompt)

        return await self._image_generator_func(enhanced_prompt)

    async def generate_and_download_images(
        self,
        storyboard_project: Dict[str, Any],
        story_dir: str,
        image_style: str
    ) -> List[str]:
        image_files = []
        characters = storyboard_project['characters']
        
        for i, storyboard in enumerate(storyboard_project['storyboards']):
            image_content = await self.generate_image(storyboard, characters, image_style)
            if image_content:
                image_filename = os.path.join(story_dir, f"scene_{storyboard['scene_number']}.png")
                storyboard['image'] = image_filename
                try:
                    with open(image_filename, 'wb') as f:
                        f.write(image_content)
                    image_files.append(image_filename)
                    print(f"Image saved for scene {storyboard['scene_number']}")
                except IOError as e:
                    print(f"Failed to save image for scene {storyboard['scene_number']}: {e}")
                    if i > 0:
                        storyboard['image'] = image_files[-1]  # Use the previous image
                    else:
                        # For the first image, create a blank image
                        create_blank_image(image_filename)
                        storyboard['image'] = image_filename
                        image_files.append(image_filename)
            else:
                print(f"Failed to generate image for scene {storyboard['scene_number']}")
                if i > 0:
                    storyboard['image'] = image_files[-1]  # Use the previous image
                else:
                    # For the first image, create a blank image
                    image_filename = os.path.join(story_dir, f"scene_{storyboard['scene_number']}.png")
                    create_blank_image(image_filename)
                    storyboard['image'] = image_filename
                    image_files.append(image_filename)
        return image_files

    async def _image_generator_func(self, prompt: str) -> Optional[bytes]:
        try:
            output = self.replicate_client.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={"prompt": prompt}
            )
            if output and isinstance(output, list) and len(output) > 0:
                image_url = output[0]
                response = requests.get(image_url)
                if response.status_code == 200:
                    return response.content
            return None
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
