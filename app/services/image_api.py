import os
import time
import aiohttp
import replicate
from typing import Optional
from app.core.config import settings

async def huggingface_flux_api(prompt: str, max_retries: int = 3) -> Optional[bytes]:
    HF_API_URL = settings.HUGGINGFACE_API_URL
    HF_HEADERS = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}

    payload = {
        "inputs": prompt,
        "parameters": {
            "width": settings.HUGGINGFACE_IMAGE_WIDTH,
            "height": settings.HUGGINGFACE_IMAGE_HEIGHT,
            "num_inference_steps": settings.HUGGINGFACE_NUM_INFERENCE_STEPS,
            "guidance_scale": settings.HUGGINGFACE_GUIDANCE_SCALE,
        },
    }

    async with aiohttp.ClientSession() as session:
        for attempt in range(max_retries):
            try:
                async with session.post(HF_API_URL, headers=HF_HEADERS, json=payload) as response:
                    response.raise_for_status()
                    return await response.read()
            except aiohttp.ClientError as e:
                if attempt < max_retries - 1:
                    print(f"Error in Hugging Face API request (attempt {attempt + 1}/{max_retries}): {e}")
                    print("Retrying...")
                    await asyncio.sleep(1)  # Wait for 1 second before retrying
                else:
                    print(f"Error in Hugging Face API request after {max_retries} attempts: {e}")
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
                print(f"Error in Flux Schnell generation (attempt {attempt + 1}/{max_retries}): {e}")
                print("Retrying...")
                await asyncio.sleep(1)  # Wait for 1 second before retrying
            else:
                print(f"Error in Flux Schnell generation after {max_retries} attempts: {e}")
    return None
