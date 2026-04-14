from abc import ABC, abstractmethod
from logging import getLogger
from typing import Generic, Optional, Type, TypeVar, Union

from sqlalchemy import delete, desc, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import Base

log = getLogger()

ModelType = TypeVar("ModelType", bound=Base)


class BaseORMHandler(Generic[ModelType], ABC):
    model_cls: Type[ModelType]
    use_unique_scalars: bool

    @classmethod
    def _get_unique_scalars(
        cls, obj
    ) -> Union[Optional[ModelType], list[Optional[ModelType]]]:
        """Делает скаляр ответа бд, в случае необходимости"""
        if cls.use_unique_scalars:
            obj = obj.unique()
        return obj

    @classmethod
    async def get(cls, session: AsyncSession, pk_value: int) -> Optional[ModelType]:
        """Получает одну определенную запись по pk_value"""

        obj = await session.get(cls.model_cls, pk_value)

        return obj

    @classmethod
    async def _get_all(cls, session: AsyncSession, query) -> list[Optional[ModelType]]:
        """Получает все существующие записи по выбранным настройкам. Является утилитой
        Желательно обставлять в try-except для более подробных логов"""
        result = await session.execute(query)
        scalars = result.scalars()
        obj_list = cls._get_unique_scalars(scalars)
        obj_list = scalars.all()

        return obj_list

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[Optional[ModelType]]:
        """Получает все существующие записи"""
        query = select(cls.model_cls)

        return await cls._get_all(session, query)

    @classmethod
    async def _insert(cls, session: AsyncSession, **kwargs) -> ModelType:
        """Служит утилитой"""
        obj = cls.model_cls(**kwargs)
        session.add(obj)
        return obj

    @classmethod
    @abstractmethod
    async def insert(cls, session: AsyncSession, **kwargs) -> ModelType:
        """Абстрактый метод, реализуйте с использованием _insert()"""

    @classmethod
    async def remove(cls, session: AsyncSession, pk_value) -> None:
        """Удаляет выбранную запись"""
        query = delete(cls.model_cls).filter_by(id=pk_value)

        await session.execute(query)
