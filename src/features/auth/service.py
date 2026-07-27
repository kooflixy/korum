from fastapi import Form, HTTPException, status

from src.db import async_session_factory
from src.features.auth.security import validate_password
from src.features.users.repository import UserRepository


async def validate_auth_user(username: str = Form(), password: str = Form()):
    unauthed_exc = HTTPException(
        status.HTTP_401_UNAUTHORIZED, detail="invalid username or password"
    )

    async with async_session_factory() as session:
        user = await UserRepository.get_by_username(session, username=username)

    if not user:
        raise unauthed_exc

    if not validate_password(password=password, hashed_password=user.hashed_password):
        raise unauthed_exc

    return user
