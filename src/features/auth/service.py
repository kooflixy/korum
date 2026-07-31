from fastapi import Depends, Form, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from src.db import async_session_factory
from src.features.auth.security import decode_jwt, validate_password
from src.features.users.repository import UserRepository
from src.features.users.schemas import UserResponse

http_bearer = HTTPBearer()


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


def get_current_token_payload(
    creds: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    token = creds.credentials
    try:
        payload = decode_jwt(token)
    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    return payload


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
) -> UserResponse:
    sub_val = payload.get("sub")

    try:
        user_id = int(sub_val)
    except (ValueError, TypeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid token")

    async with async_session_factory() as session:
        user = await UserRepository.get_by_id(session, user_id)

    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid token")

    return user
