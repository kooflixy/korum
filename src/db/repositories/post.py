from logging import getLogger
from typing import Optional

from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.db.database import async_session_factory
from src.db.models import PostORM
from src.db.repositories import BaseRepository

log = getLogger(__name__)


class PostRepository(BaseRepository[PostORM]):
    model_cls = PostORM
    use_unique_scalars = True

    @classmethod
    async def insert(cls, session: AsyncSession, title: str, content: str) -> PostORM:
        """Делает запись и возвращает записанный объект"""

        obj = await cls._insert(session, title=title, content=content)

        return obj

    @classmethod
    async def get_page(
        cls,
        session: AsyncSession,
        page: int,
        sort_by: str = "id",
        order_by: str = "desc",
        on_page: int = settings.RECORDS_COUNT_ON_PAGE,
    ) -> list[PostORM]:
        order_column = cls.get_order_column_and_order(order_by, sort_by)
        query = (
            select(cls.model_cls)
            .order_by(order_column)
            .offset(on_page * ((page - 1)))
            .limit(on_page)
        )

        obj_list = (await session.execute(query)).scalars().all()
        return obj_list

    @classmethod
    async def is_last_page(
        cls,
        session: AsyncSession,
        page: int,
        sort_by: str = "id",
        order_by: str = "desc",
        on_page: int = settings.RECORDS_COUNT_ON_PAGE,
    ) -> bool:
        return (
            await cls.get_page(
                session,
                page=page + 1,
                sort_by=sort_by,
                order_by=order_by,
                on_page=on_page,
            )
        ) == []
