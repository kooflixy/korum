from logging import getLogger
from typing import Optional

from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
