import json
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Faceless Video Generation API"
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Make these fields optional
    R2_BUCKET_NAME: str | None = None
    DATABASE_URL: str | None = None
    DATABASE_KEY: str | None = None
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_API_KEY: str | None = None
    HUGGINGFACE_API_KEY: str | None = None
    REPLICATE_API_KEY: str | None = None
    replicate_api_token: str | None = None
    SECRET_KEY: str | None = None

    # Admin user settings
    ADMIN_USERNAME: str | None = None
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None
    
    # other config items
    STORY_DIR: str = ""
    ALGORITHM: str = "HS256"
    
    # JSON config items
    story_generation: dict = {}
    storyboard: dict = {}
    azure_openai: dict = {}
    huggingface_flux_api: dict = {}
    replicate_flux_api: dict = {}
    tts: dict = {}
    azure_api_version: str = ""

    @field_validator('STORY_DIR', mode='before')
    def set_story_dir(cls, v, info):
        return v or os.path.join(info.data.get('BASE_DIR', ''), "data")

    @field_validator('story_generation', 'storyboard', 'azure_openai', 'huggingface_flux_api', 'replicate_flux_api', 'tts', 'azure_api_version', mode='before')
    def load_json_config(cls, v, info):
        if not v:
            config_path = os.path.join(info.data.get('BASE_DIR', ''), 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config.get(info.field_name, {})
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'allow'  # Add this line to allow extra fields

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300

settings = Settings()