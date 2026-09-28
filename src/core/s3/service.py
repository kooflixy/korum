from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiobotocore.response import StreamingBody
from aiobotocore.session import AioBaseClient, get_session

from src.core.config import settings


class S3Service:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[AioBaseClient, None]:
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file: bytes, object_key: str) -> None:
        async with self.get_client() as client:
            await client.put_object(Bucket=self.bucket_name, Key=object_key, Body=file)

    async def get_file(self, object_key: str) -> StreamingBody:
        async with self.get_client() as client:
            resp = await client.get_object(Bucket=self.bucket_name, Key=object_key)
            return resp["Body"]

    async def remove_file(self, object_key: str):
        async with self.get_client() as client:
            await client.delete_object(Bucket=self.bucket_name, Key=object_key)


s3_service = S3Service(
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    endpoint_url=settings.S3_ENDPOINT_URL,
    bucket_name=settings.S3_BUCKET,
)
