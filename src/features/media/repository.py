from logging import getLogger
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.repository import BaseRepository
from src.features.media.model import MediaORM, MediaStatus

log = getLogger(__name__)


class MediaRepository(BaseRepository[MediaORM]):
    model_cls = MediaORM
    use_unique_scalars = True

    @classmethod
    async def insert(
        cls,
        session: AsyncSession,
        file_key: str,
        post_id: int,
        status: MediaStatus.READY,
    ) -> MediaORM:
        """Делает запись и возвращает записанный объект"""

        obj = await cls._insert(
            session, file_key=file_key, post_id=post_id, status=status
        )

        return obj
