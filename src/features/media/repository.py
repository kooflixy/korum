from logging import getLogger
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
        status: MediaStatus = MediaStatus.READY,
    ) -> MediaORM:
        """Делает запись и возвращает записанный объект"""

        obj = await cls._insert(
            session, file_key=file_key, post_id=post_id, status=status
        )

        return obj

    @classmethod
    async def get_by_key(cls, session: AsyncSession, key: str) -> Optional[MediaORM]:
        query = (
            select(cls.model_cls)
            .filter_by(file_key=key)
            .options(selectinload(cls.model_cls.post))
        )

        obj = (await session.execute(query)).scalar()
        return obj

    @classmethod
    async def remove_by_key(cls, session: AsyncSession, key: str) -> None:
        query = delete(cls.model_cls).filter_by(file_key=key)

        obj = await session.execute(query)
        return obj

    @classmethod
    async def remove_many_by_key(cls, session: AsyncSession, keys: list[str]) -> None:
        query = delete(cls.model_cls).filter(cls.model_cls.file_key.in_(keys))

        obj = await session.execute(query)
        return obj
