from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from src.core.s3 import s3_service

router = APIRouter(tags=["Media"])


@router.get("/media/{object_key}")
async def get_media(object_key: str):
    try:
        response = await s3_service.get_file(object_key)
        body = response["Body"]
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchKey":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Медиафайл не найден"
            )
        raise exc

    return StreamingResponse(
        s3_service.get_chunk(body),
        media_type=response.get(
            "ContentType",
            "application/octet-stream",
        ),
    )
