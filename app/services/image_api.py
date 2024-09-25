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

async def fal_flux_api(task_id: str, prompt: str, seed: int = 6252023, image_size: str = "landscape_4_3", num_images: int = 1):
    try:
        # Submit the task to fal.ai
        handler = await fal_client.submit_async(
            "fal-ai/flux/dev",
            arguments={
                "prompt": prompt,
                "seed": seed,
                "image_size": image_size,
                "num_images": num_images
            },
        )

        # Update task status to "processing"
        await ImageTask.update(task_id, status="processing")

        log_index = 0
        async for event in handler.iter_events(with_logs=True):
            if isinstance(event, fal_client.InProgress):
                new_logs = event.logs[log_index:]
                for log in new_logs:
                    logger.info(f"Task {task_id}: {log['message']}")
                log_index = len(event.logs)
                
                # Update task progress (assuming the logs contain progress information)
                progress = len(event.logs) / 10  # This is a placeholder, adjust based on actual log structure
                await ImageTask.update(task_id, progress=progress)

        # Get the final result
        result = await handler.get()
        
        # Update task with the result
        image_urls = [image['url'] for image in result.get('images', [])]
        await ImageTask.update(task_id, status="completed", images=image_urls)

        return result

    except Exception as e:
        logger.error(f"Error in fal_flux_api for task {task_id}: {str(e)}")
        await ImageTask.update(task_id, status="failed")
        raise

async def process_image_task(task_id: str):
    task = await ImageTask.get(task_id)
    if not task:
        logger.error(f"Task {task_id} not found")
        return

    try:
        result = await fal_flux_api(
            task_id=task.id,
            prompt=f"{task.story_topic} in {task.art_style} style",
            num_images=1  # Adjust as needed
        )
        logger.info(f"Task {task_id} completed successfully")
    except Exception as e:
        logger.error(f"Failed to process task {task_id}: {str(e)}")
        await ImageTask.update(task_id, status="failed")

if __name__ == "__main__":
    asyncio.run(process_image_task("your_task_id_here"))