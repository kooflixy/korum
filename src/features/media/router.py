from aiobotocore.client import AioBaseClient
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.core.s3 import s3_service

router = APIRouter(tags=["Media"])


@router.get("/media/{object_key}")
async def get_media(object_key: str):
    try:
        s3_file = await s3_service.get_file(object_key)
    except ClientError as exc:
        if exc.response["Error"]["Code"] in ("NoSuchKey", "404", "NotFound"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Медиафайл не найден"
            )
        raise exc

    return Response(content=s3_file.content, media_type=s3_file.media_type)
