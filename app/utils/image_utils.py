import os
import aiohttp
from app.core.logging import logger

async def download_and_save_image(image_url: str, save_path: str) -> bool:
    """
    Download an image from the given URL and save it to the specified path.
    
    Args:
    image_url (str): The URL of the image to download.
    save_path (str): The full path where the image should be saved.
    
    Returns:
    bool: True if the image was successfully downloaded and saved, False otherwise.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    with open(save_path, "wb") as f:
                        f.write(image_data)
                    return True
                else:
                    logger.error(f"Failed to download image from {image_url}. Status code: {response.status}")
                    return False
    except Exception as e:
        logger.error(f"Error downloading image from {image_url}: {str(e)}")
        return False