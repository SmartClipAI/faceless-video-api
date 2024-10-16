import boto3
from app.core.config import settings
from app.core.logging import logger
from typing import Optional

class StorageService:
    def __init__(self):
        self.r2_client = boto3.client(
            's3',
            endpoint_url=settings.R2_ENDPOINT,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY
        )

    async def upload_to_r2(self, file_path: str, object_name: str) -> Optional[str]:
        try:
            self.r2_client.upload_file(file_path, settings.R2_BUCKET_NAME, object_name)
            # url = f"{settings.R2_ENDPOINT}/{settings.R2_BUCKET_NAME}/{object_name}"
            # for public access
            url = f"{settings.R2_PUBLIC_ENDPOINT}/{object_name}"
            logger.info(f"File uploaded successfully to R2: {url}")
            return url
        except Exception as e:
            logger.error(f"Error uploading file to R2: {str(e)}")
            return None