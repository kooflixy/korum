from logging import getLogger
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config import settings
from src.core.repository import BaseRepository
from src.features.auth.model import RefreshTokenORM

log = getLogger(__name__)


class RefreshTokenRepository(BaseRepository[RefreshTokenORM]):
    model_cls = RefreshTokenORM
    use_unique_scalars = True

    @classmethod
    async def insert(
        cls,
        session: AsyncSession,
        user_id: int,
        token_hash: bytes,
        ip_address: Optional[str],
        device_info: Optional[str],
    ) -> RefreshTokenORM:
        """Делает запись и возвращает записанный объект"""

        obj = await cls._insert(
            session,
            user_id=user_id,
            token_hash=token_hash,
            ip_address=ip_address,
            device_info=device_info,
        )

        return obj

    @classmethod
    async def get_by_hash(
        cls, session: AsyncSession, token_hash: bytes
    ) -> RefreshTokenORM:
        query = (
            select(cls.model_cls)
            .filter_by(token_hash=token_hash)
            .options(selectinload(cls.model_cls.user))
        )
        obj = (await session.execute(query)).scalar()
        return obj

    @classmethod
    async def revoke_all_user_tokens(cls, session: AsyncSession, user_id: int) -> None:
        query = (
            update(cls.model_cls)
            .filter_by(user_id=user_id, is_revoked=False)
            .values(is_revoked=True)
        )

        await session.execute(query)
