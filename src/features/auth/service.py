from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_async_session
from src.features.auth.repository import RefreshTokenRepository
from src.features.auth.schemas import TokenInfo
from src.features.auth.security import (
    decode_jwt,
    encode_jwt,
    generate_refresh_token,
    hash_refresh_token,
    validate_password,
)
from src.features.users.repository import UserRepository
from src.features.users.schemas import UserResponse

http_bearer = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def validate_auth_user(
    username: str = Form(""),
    password: str = Form(""),
    session: AsyncSession = Depends(get_async_session),
):
    unauthed_exc = HTTPException(
        status.HTTP_401_UNAUTHORIZED, detail="invalid username or password"
    )

    username = username.strip()

    if not username or not password:
        raise unauthed_exc

    user = await UserRepository.get_by_username(session, username=username)

    if not user:
        raise unauthed_exc

    if not validate_password(password=password, hashed_password=user.hashed_password):
        raise unauthed_exc

    return user


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    # token = creds.credentials
    try:
        payload = decode_jwt(token)
    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    return payload


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(get_async_session),
) -> UserResponse:
    sub_val = payload.get("sub")

    try:
        user_id = int(sub_val)
    except (ValueError, TypeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid token")

    user = await UserRepository.get_by_id(session, user_id)

    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid token")

    return user


async def create_user_session(
    session: AsyncSession, user_id: int, username: str, request: Request
) -> TokenInfo:
    jwt_payload = {"sub": str(user_id), "username": username}
    access_token = encode_jwt(jwt_payload)

    refresh_token = generate_refresh_token()

    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    await RefreshTokenRepository.insert(
        session,
        user_id=user_id,
        token_hash=hash_refresh_token(refresh_token),
        ip_address=ip_address,
        device_info=user_agent,
    )

    return TokenInfo(
        access_token=access_token, refresh_token=refresh_token, token_type="Bearer"
    )
