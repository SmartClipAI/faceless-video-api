import os
import asyncio
from moviepy.editor import (
    ImageClip,
    concatenate_videoclips,
    AudioFileClip
)
from app.services.audio_generator import AudioGenerator
from app.utils.transitions import zoom 
import shortcap
from app.core.config import settings
from app.core.logging import logger
from app.utils.image_utils import download_image

class VideoGenerator:
    def __init__(self, client):
        self.audio_generator = AudioGenerator(client)
        self.font_path = os.path.join(settings.BASE_DIR, "resources/fonts")

    async def add_captions(self, output_file, output_file_subtitle):
        shortcap.add_captions(
            video_file=output_file,
            output_file=output_file_subtitle,
            font=os.path.join(self.font_path, "TitanOne.ttf"),
            font_size=70,
            font_color="white",
            stroke_width=3,
            stroke_color="black",
            shadow_strength=1.0,
            shadow_blur=0.1,
            highlight_current_word=True,
            word_highlight_color="yellow",
            line_count=1,
            padding=70,
            position="bottom",
            use_local_whisper=False,
        )

    async def generate_video(self, storyboard_project, story_dir, voice_name):
        audio_dir = os.path.join(story_dir, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        video_path = os.path.join(story_dir, "story_video.mp4")
        clips = []
        try:
            for scene in storyboard_project['storyboards']:
                # Generate audio for the subtitle
                audio_file = os.path.join(audio_dir, f"scene_{scene['scene_number']}.mp3")
                success = await self.audio_generator.generate_audio(scene['subtitles'], audio_file, voice_name)
                if not success:
                    logger.error(f"Failed to generate audio for scene {scene['scene_number']}")
                    continue

                # Create audio clip
                audio_clip = AudioFileClip(audio_file)
                
                # Download and use the image
                image_path = os.path.join(story_dir, f"scene_{scene['scene_number']}.png")
                downloaded_image = await download_image(scene['image'], image_path)
                
                if downloaded_image is None:
                    logger.error(f"Skipping scene {scene['scene_number']} due to image download failure")
                    continue
                
                # Create image clip with duration matching the audio
                image_clip = ImageClip(downloaded_image).set_duration(audio_clip.duration)
                
                # Combine image, text, and audio
                video_clip = image_clip.set_audio(audio_clip)

                # Apply transition effect
                transition_type = scene['transition_type']
                    
                if transition_type == 'zoom-in':
                    clips.append(zoom(video_clip))
                elif transition_type == 'zoom-out':
                    clips.append(zoom(video_clip, mode='out'))
                else:
                    clips.append(video_clip)

            if not clips:
                logger.error("No valid clips generated")
                return None

            final_clip = concatenate_videoclips(clips)
            
            # Use a separate thread for video writing to avoid blocking the event loop
            await asyncio.to_thread(final_clip.write_videofile, video_path, fps=24)

            subtitle_video_path = video_path.replace('.mp4', '_subtitle.mp4')
            await self.add_captions(video_path, subtitle_video_path)

            return subtitle_video_path
        except Exception as e:
            logger.error(f"Error in generate_video: {str(e)}")
            return None
