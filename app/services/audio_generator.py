import os
from openai import AzureOpenAI
from app.core.config import settings

class AudioGenerator:
    def __init__(self, client: AzureOpenAI):
        self.client = client
        self.speech_rate = settings.tts['speech_rate']

    async def generate_audio(self, text: str, output_file: str, voice_name: str) -> bool:
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

            print(f"Speech synthesized for text [{text}], and the audio was saved to [{output_file}]")
            return True

        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            return False
