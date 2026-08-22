from logging import getLogger
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config import settings
from src.core.repository import BaseRepository
from src.features.posts.model import PostORM

log = getLogger(__name__)


class PostRepository(BaseRepository[PostORM]):
    model_cls = PostORM
    use_unique_scalars = True

    @classmethod
    async def insert(
        cls, session: AsyncSession, title: str, content: str, author_id: int
    ) -> PostORM:
        """Делает запись и возвращает записанный объект"""

        obj = await cls._insert(
            session, title=title, content=content, author_id=author_id
        )

        return obj

    @classmethod
    async def update(
        cls, session: AsyncSession, post_id: int, update_data: BaseModel
    ) -> PostORM:

        data = update_data.model_dump(exclude_unset=True)

        obj = await cls._update(session, pk_value=post_id, **data)

        return obj

    @classmethod
    async def get(cls, session: AsyncSession, id: int) -> Optional[PostORM]:
        query = (
            select(cls.model_cls)
            .filter_by(id=id)
            .options(selectinload(cls.model_cls.author))
        )

        obj = (await session.execute(query)).scalar()
        return obj

    @classmethod
    async def delete(cls, session: AsyncSession, id: int) -> None:
        post = await cls.get(session, id)
        if post:
            post.is_deleted = True

    @classmethod
    async def delete_object(cls, session: AsyncSession, post: PostORM) -> None:
        post.is_deleted = True

    @classmethod
    async def get_page(
        cls,
        session: AsyncSession,
        page: int,
        per_page: int = settings.RECORDS_COUNT_ON_PAGE,
        sort_by: str = "id",
        order_by: str = "desc",
    ) -> list[PostORM]:
        order_column = cls.get_order_column_and_order(order_by, sort_by)
        query = (
            select(cls.model_cls)
            .filter_by(is_deleted=False)
            .order_by(order_column)
            .offset(per_page * (page - 1))
            .limit(per_page + 1)
            .options(selectinload(cls.model_cls.author))
        )

        obj_list = (await session.execute(query)).scalars().all()
        return obj_list
