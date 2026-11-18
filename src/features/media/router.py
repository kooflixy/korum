from botocore.exceptions import ClientError
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.s3 import s3_service
from src.core.s3.utils import generate_uuid_filename
from src.db import get_async_session
from src.features.auth.service import get_current_auth_user
from src.features.media.repository import MediaRepository
from src.features.media.schemas import MediaResponse
from src.features.media.service import ValidatedFile, validate_file
from src.features.posts.repository import PostRepository
from src.features.users.schemas import UserResponse

router = APIRouter(prefix="/media", tags=["Media"])


@router.get("/{object_key}")
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


@router.delete("/{object_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    object_key: str,
    user: UserResponse = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_async_session),
):
    obj = await MediaRepository.get_by_key(session, object_key)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Медиафайл не найден"
        )

    if obj.post.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь автором поста, к которому прикреплен медиафайл",
        )

    try:
        await MediaRepository.remove_by_key(session, object_key)
        await s3_service.remove_file(object_key)

        await session.commit()
    except ClientError as exc:
        await session.rollback()

        if exc.response["Error"]["Code"] in ("NoSuchKey", "404", "NotFound"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Медиафайл не найден"
            )
        raise exc


@router.post("/upload", response_model=MediaResponse)
async def upload_media(
    post_id: int,
    uploaded_media: ValidatedFile = Depends(
        validate_file(
            settings.MAX_POST_MEDIAFILE_SIZE, settings.ALLOWED_POST_MIME_TYPES
        )
    ),
    user: UserResponse = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_async_session),
):
    post = await PostRepository.get(session, post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост для прикрепления медифайла не найден",
        )

    if post.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь автором поста",
        )

    object_key = generate_uuid_filename(uploaded_media.mime_type)

    await s3_service.upload_file(
        await uploaded_media.file.read(),
        object_key,
        uploaded_media.mime_type,
    )

    try:
        media_record = await MediaRepository.insert(
            session, file_key=object_key, post_id=post_id
        )

        await session.commit()
    except Exception:
        await session.rollback()
        await s3_service.remove_file(object_key)

        raise

    return media_record
