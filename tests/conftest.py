import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from src.core.config import settings
from src.db import get_async_session
from src.features.auth.repository import RefreshTokenRepository
from src.features.auth.schemas import UserCreate
from src.features.auth.security import (
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
)
from src.features.posts.repository import PostRepository
from src.features.users.repository import UserRepository
from src.main import app

test_engine = create_async_engine(settings.DATABASE_URL_asyncpg, poolclass=NullPool)


@pytest.fixture(scope="session", autouse=True)
def db_migrations():
    alembic_cfg = Config("alembic.ini")

    command.upgrade(alembic_cfg, "head")


@pytest_asyncio.fixture()
async def session():
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        async with AsyncSession(bind=connection, expire_on_commit=False) as session:
            yield session

        await transaction.rollback()


@pytest_asyncio.fixture()
async def base_data(session):
    created_data = dict()
    users = [
        UserCreate(username="user1", password="password1"),
        UserCreate(username="user2", password="password2"),
        UserCreate(username="user3", password="password3"),
    ]

    for user in users:
        new_user = await UserRepository.insert(
            session,
            username=user.username,
            hashed_password=hash_password(user.password),
        )
        created_data[new_user.username] = new_user

    await session.flush()

    for user in users:
        user = created_data[user.username]
        refresh_token = generate_refresh_token()
        await RefreshTokenRepository.insert(
            session,
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            ip_address=f"127.0.0.1",
            device_info=f"{user.username}_user_agent",
        )
        created_data[f"{user.username}_refresh_token"] = refresh_token

    await session.flush()
    #fmt: off
    posts = [
        dict(title="post1",  content="content1",  author_id=created_data["user1"].id),
        dict(title="post2",  content="content2",  author_id=created_data["user2"].id, is_deleted=True),
        dict(title="post3",  content="content3",  author_id=created_data["user3"].id),
        dict(title="post4",  content="content4",  author_id=created_data["user2"].id),
        dict(title="post5",  content="content5",  author_id=created_data["user3"].id, is_deleted=True),
        dict(title="post6",  content="content6",  author_id=created_data["user2"].id),
        dict(title="post7",  content="content7",  author_id=created_data["user1"].id),
        dict(title="post8",  content="content8",  author_id=created_data["user3"].id, is_deleted=True),
        dict(title="post9",  content="content9",  author_id=created_data["user1"].id),
        dict(title="post10", content="content10", author_id=created_data["user3"].id),
        dict(title="post11", content="content10", author_id=created_data["user2"].id),
        dict(title="post12", content="content10", author_id=created_data["user3"].id, is_deleted=True),
        dict(title="post13", content="content10", author_id=created_data["user1"].id),
        dict(title="post14", content="content10", author_id=created_data["user2"].id),
        dict(title="post15", content="content10", author_id=created_data["user1"].id),
        dict(title="post16", content="content10", author_id=created_data["user2"].id),
        dict(title="post17", content="content10", author_id=created_data["user1"].id),
        dict(title="post18", content="content10", author_id=created_data["user1"].id, is_deleted=True),
        dict(title="post19", content="content10", author_id=created_data["user3"].id),
    ]
    #fmt: on

    for post in posts:
        new_post = await PostRepository.insert(
            session,
            title=post["title"],
            content=post["content"],
            author_id=post["author_id"],
        )
        if post.get("is_deleted"):
            new_post.is_deleted = True
        created_data[new_post.title] = new_post

    await session.flush()

    return created_data


@pytest_asyncio.fixture()
async def client(session):
    app.dependency_overrides[get_async_session] = lambda: session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
