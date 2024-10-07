import os
import asyncio
from openai import AsyncAzureOpenAI
from app.core.config import settings
from app.core.logging import logger

class AudioGenerator:
    def __init__(self, client: AsyncAzureOpenAI):
        self.client = client
        self.speech_rate = settings.tts.get('speech_rate', 1.0)  # Default to 1.0 if not found
        self.delay = settings.tts.get('delay', 1.0)  # Default delay of 1 second, configurable in settings

    async def generate_audio(self, text: str, output_file: str, voice_name: str) -> bool:
        # Add delay before generating audio
        await asyncio.sleep(self.delay)

        try:
            result = await self.client.audio.speech.create(
                model="tts",
                voice=voice_name,
                input=text,
                speed=self.speech_rate,
                response_format="mp3"
            )
            # Save the audio content to the output file
            with open(output_file, "wb") as audio_file:
                audio_file.write(result.content)

            logger.info(f"Speech synthesized for text [{text}], and the audio was saved to [{output_file}]")
            return True

        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            return False

   
