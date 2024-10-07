import json
from pydantic_settings import BaseSettings
from pydantic import field_validator
from app.core.logging import logger
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
    AZURE_SPEECH_KEY: str | None = None
    AZURE_SPEECH_REGION: str | None = None
    HUGGINGFACE_API_KEY: str | None = None
    REPLICATE_API_KEY: str | None = None
    replicate_api_token: str | None = None
    SECRET_KEY: str | None = None
    FAL_KEY: str | None = None

    # Admin user settings
    ADMIN_USERNAME: str | None = None
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None
    
    # other config items
    STORY_DIR: str = ""
    ALGORITHM: str = "HS256"
    
    # JSON config items
    story_limit_short: dict | None = None
    story_limit_long: dict | None = None
    storyboard: dict | None = None
    azure_openai: dict | None = None
    fal_flux_dev_api: dict | None = None
    fal_flux_schnell_api: dict | None = None
    replicate_flux_api: dict | None = None
    tts: dict | None = None
    azure_api_version: str | None = None
    use_fal_flux: bool | None = None
    use_fal_flux_dev: bool | None = None


    @field_validator('STORY_DIR', mode='before')
    def set_story_dir(cls, v, info):
        return v or os.path.join(os.path.dirname(info.data.get('BASE_DIR', '')), "data")

    @field_validator('story_limit_short', 'story_limit_long', 'storyboard', 'azure_openai', 'fal_flux_dev_api', 'fal_flux_schnell_api', 'replicate_flux_api', 'tts', 'azure_api_version', 'use_fal_flux', 'use_fal_flux_dev', mode='before')
    def load_json_config(cls, v, info):
        if v is None or (isinstance(v, (str, dict)) and not v):
            config_path = os.path.join(os.path.dirname(info.data.get('BASE_DIR', '')), 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            loaded_value = config.get(info.field_name)
            logger.info(f"Loaded value for {info.field_name}: {loaded_value}")
            return loaded_value
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'allow'  # Add this line to allow extra fields

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 365 * 10  # 10 years

settings = Settings()