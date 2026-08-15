import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config

from src.db import async_session_factory


@pytest.fixture(scope="session", autouse=True)
def db_migrations():
    alembic_cfg = Config("alembic.ini")

    command.upgrade(alembic_cfg, "head")

    # yield

    # command.downgrade(alembic_cfg, 'base')


@pytest_asyncio.fixture
async def session():
    async with async_session_factory() as session:
        yield session
        await session.rollback()
