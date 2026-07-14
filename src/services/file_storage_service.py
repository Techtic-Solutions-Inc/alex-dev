import os
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class FileStorageService:
    """
    Service for handling file storage and retrieval.
    """

    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv('S3_BUCKET_NAME')

    async def store_file(self, file: UploadFile) -> str:
        """
        Store a file in S3 and return the file URL.

        - **file**: The file to store.
        """
        try:
            file_key = f"uploads/{file.filename}"
            self.s3_client.upload_fileobj(file.file, self.bucket_name, file_key)
            file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"
            logger.info(f"File stored successfully: {file_url}")
            return file_url
        except ClientError as e:
            logger.error(f"Failed to store file: {e}")
            raise

    def generate_secure_url(self, file_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a secure URL for accessing a file.

        - **file_key**: The key of the file in S3.
        - **expiration**: Time in seconds until the URL expires.
        """
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            logger.info(f"Generated secure URL: {response}")
            return response
        except ClientError as e:
            logger.error(f"Failed to generate secure URL: {e}")
            return None