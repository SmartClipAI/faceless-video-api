import asyncio
import aiohttp
import replicate
import ssl
from typing import Optional
from app.core.config import settings
from app.core.logging import logger

async def huggingface_flux_api(prompt: str, max_retries: int = 3) -> Optional[bytes]:
    HF_API_URL = settings.huggingface_flux_api.get('url')
    HF_HEADERS = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}

    payload = {
        "inputs": prompt,
        "parameters": {
            "width": settings.huggingface_flux_api.get('width'),
            "height": settings.huggingface_flux_api.get('height'),
            "num_inference_steps": settings.huggingface_flux_api.get('num_inference_steps'),
            "guidance_scale": settings.huggingface_flux_api.get('guidance_scale'),
        },
    }

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        for attempt in range(max_retries):
            try:
                async with session.post(HF_API_URL, headers=HF_HEADERS, json=payload) as response:
                    response.raise_for_status()
                    return await response.read()
            except aiohttp.ClientError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error in Hugging Face API request (attempt {attempt + 1}/{max_retries}): {e}")
                    logger.info("Retrying...")
                    await asyncio.sleep(1)  # Wait for 1 second before retrying
                else:
                    logger.error(f"Error in Hugging Face API request after {max_retries} attempts: {e}")
    return None

async def replicate_flux_api(prompt: str, max_retries: int = 3) -> Optional[bytes]:
    payload = {
        "prompt": prompt,
        "aspect_ratio": settings.REPLICATE_ASPECT_RATIO,
        "num_inference_steps": settings.REPLICATE_NUM_INFERENCE_STEPS,
        "guidance": settings.REPLICATE_GUIDANCE,
        "output_quality": settings.REPLICATE_OUTPUT_QUALITY,
    }

    for attempt in range(max_retries):
        try:
            image_urls = replicate.run(
                settings.REPLICATE_MODEL,
                input=payload
            )
            if image_urls and isinstance(image_urls, list) and len(image_urls) > 0:
                image_url = image_urls[0]
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as response:
                        response.raise_for_status()
                        return await response.read()
            else:
                raise ValueError("No image URL returned from Replicate API")
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Error in Flux Schnell generation (attempt {attempt + 1}/{max_retries}): {e}")
                logger.info("Retrying...")
                await asyncio.sleep(1)  # Wait for 1 second before retrying
            else:
                logger.error(f"Error in Flux Schnell generation after {max_retries} attempts: {e}")
    return None
