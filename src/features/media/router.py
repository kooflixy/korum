import magic
from botocore.exceptions import ClientError
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.s3 import s3_service
from src.core.s3.utils import generate_uuid_filename
from src.db import get_async_session
from src.features.auth.service import get_current_auth_user
from src.features.media.repository import MediaRepository
from src.features.media.schemas import MediaResponse
from src.features.posts.repository import PostRepository
from src.features.users.schemas import UserResponse

MAX_POST_MEDIAFILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_MIME_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
]

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


@router.post("/media/upload", response_model=MediaResponse)
async def upload_media(
    post_id: int,
    uploaded_media: UploadFile = File(...),
    user: UserResponse = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_async_session),
):
    mime_type = magic.from_buffer(await uploaded_media.read(2048), mime=True)

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Неподдерживаемый формат медиафайла",
        )

    if uploaded_media.size and uploaded_media.size > MAX_POST_MEDIAFILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Медиафайл слишком большой",
        )

    await uploaded_media.seek(0)

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

    object_key = generate_uuid_filename(mime_type)

    try:
        media_record = await MediaRepository.insert(
            session, file_key=object_key, post_id=post_id
        )

        await s3_service.upload_file(
            await uploaded_media.read(), object_key, media_type=mime_type
        )

        await session.commit()
    except Exception:
        await session.rollback()
        await MediaRepository.remove(session, media_record.id)

        raise

    return media_record
