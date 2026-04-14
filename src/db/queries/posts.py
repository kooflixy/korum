from logging import getLogger
from typing import Optional

from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.db.database import async_session_factory
from src.db.models import PostsORM
from src.db.queries import BaseORMHandler

log = getLogger(__name__)


class PostsORMHandler(BaseORMHandler[PostsORM]):
    model_cls = PostsORM
    use_unique_scalars = True

    @classmethod
    async def insert(cls, session: AsyncSession, title: str, content: str):
        """Делает запись и возвращает записанный объект"""

        obj = await cls._insert(session, title=title, content=content)

        return obj

    @classmethod
    async def get_page(
        cls,
        session: AsyncSession,
        page: int,
        on_page: int = settings.RECORDS_COUNT_ON_PAGE,
    ):
        query = select(cls.model_cls).offset(on_page * ((page - 1))).limit(on_page)

        obj_list = (await session.execute(query)).scalars().all()
        return obj_list

    @classmethod
    async def is_last_page(
        cls,
        session: AsyncSession,
        page: int,
        on_page: int = settings.RECORDS_COUNT_ON_PAGE,
    ):
        return (await cls.get_page(session, page=page + 1, on_page=on_page)) == []
