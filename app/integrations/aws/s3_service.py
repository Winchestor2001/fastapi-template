import hashlib
from io import BytesIO

import aioboto3
from fastapi import UploadFile

from app.core.settings import settings
from loggers import get_logger

logger = get_logger(__name__)


class S3Service:
    def __init__(self):
        self.bucket_name = settings.bucket_name
        self.sample_url = settings.s3_sample_url
        self.aws_access_key_id = settings.aws_access_key_id
        self.aws_secret_access_key = settings.aws_secret_access_key
        self.region_name = settings.region_name
        self.s3_session = None

    async def __aenter__(self):
        """
        Initializes the S3 client when entering the async context.
        """
        try:
            self.s3_session = aioboto3.Session()
            self.s3_client = await self.s3_session.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            ).__aenter__()
            return self
        except Exception as e:
            logger.error("Failed to initialize S3 client: %s", e)
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the S3 client when exiting the async context.
        """
        try:
            if self.s3_client:
                await self.s3_client.__aexit__(exc_type, exc_val, exc_tb)
        except Exception as e:
            logger.error("Failed to close S3 client: %s", e)

    async def upload_file(self, file_data: bytes, file_name: str) -> str:
        """
        Uploads a binary file to the S3 bucket.

        :param file_data: Binary content of the file.
        :param file_name: Original file name to generate the key.
        :return: URL of the uploaded file.
        """
        key = await self.generate_hashed_name(file_data, file_name)
        try:
            await self.s3_client.upload_fileobj(BytesIO(file_data), self.bucket_name, key)
            return self.sample_url.format(self.bucket_name, key)
        except Exception as e:
            logger.error("Failed to upload file: %s", e)
            raise


    async def upload_uploadfile(self, file: UploadFile) -> str:
        """
        Uploads an UploadFile object to the S3 bucket.

        :param file: FastAPI UploadFile object.
        :return: URL of the uploaded file.
        """
        file_data = await file.read()
        key = await self.generate_hashed_name(file_data, file.filename)
        try:
            await self.s3_client.upload_fileobj(BytesIO(file_data), self.bucket_name, key)
            return self.sample_url.format(self.bucket_name, key)
        except Exception as e:
            logger.error("Failed to upload UploadFile: %s", e)
            raise

    async def delete_file(self, key: str) -> None:
        """
        Deletes a file from the S3 bucket.

        :param key: Key (path) of the file in S3.
        """
        try:
            await self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        except Exception as e:
            logger.error("Failed to delete file: %s", e)
            raise

    @staticmethod
    async def generate_hashed_name(file_data: bytes, file_name: str) -> str:
        """
        Generates a hashed name for a file using its contents.

        :param file_data: Binary content of the file.
        :param file_name: Original file name to extract the extension.
        :return: Hashed name with the original file extension.
        """
        try:
            file_hash = hashlib.sha256(file_data).hexdigest()
            file_extension = file_name.split('.')[-1]
            return f"{file_hash}.{file_extension}"
        except Exception as e:
            logger.error("Failed to generate hashed name: %s", e)
            raise