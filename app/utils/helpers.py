import os
from datetime import datetime
from typing import Dict, Any
from PIL import Image


def create_resource_dir(base_dir: str, story_type: str, title: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
    dir_name = f"{timestamp}_{story_type}_{safe_title[:50]}"
    full_path = os.path.join(base_dir, dir_name)
    os.makedirs(full_path, exist_ok=True)
    return full_path

async def call_azure_openai_api(client, messages):
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling Azure OpenAI API: {e}")
        return None

def create_empty_storyboard(title: str) -> Dict[str, Any]:
    return {
        "project_info": {
            "title": title,
            "user": "AI Generated",
            "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        },
        "storyboards": []
    }

def create_blank_image(filename, width=720, height=1280):
    blank_image = Image.new('RGB', (width, height), color='black')
    blank_image.save(filename)
    print(f"Created blank image: {filename}")
