from logging import getLogger
from typing import Optional

from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.db.database import async_session_factory
from src.db.models import UserORM
from src.db.repositories import BaseRepository

log = getLogger(__name__)


class UserRepository(BaseRepository[UserORM]):
    model_cls = UserORM
    use_unique_scalars = True

    @classmethod
    async def insert(
        cls, session: AsyncSession, username: str, hashed_password: bytes
    ) -> UserORM:
        """Делает запись и возвращает записанный объект"""

        obj = await cls._insert(
            session, username=username, hashed_password=hashed_password
        )

        return obj

    @classmethod
    async def get_by_id(
        cls,
        session: AsyncSession,
        id: int,
    ) -> Optional[UserORM]:
        return cls.get(session, id)

    @classmethod
    async def get_by_username(
        cls,
        session: AsyncSession,
        username: str,
    ) -> Optional[UserORM]:
        query = select(cls.model_cls).filter_by(username=username)

        obj = (await session.execute(query)).scalar()
        return obj
