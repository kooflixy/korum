from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_async_session
from src.features.auth.repository import RefreshTokenRepository
from src.features.auth.schemas import TokenInfo, TokenRefresh, UserCreate
from src.features.auth.security import (
    hash_password,
    hash_refresh_token,
)
from src.features.auth.service import (
    create_user_session,
    get_current_auth_user,
    validate_auth_user,
)
from src.features.users.repository import UserRepository
from src.features.users.schemas import UserResponse

router = APIRouter(prefix="/auth")


@router.post("/register", status_code=status.HTTP_201_CREATED, tags=["Auth"])
async def register(
    new_user: UserCreate, session: AsyncSession = Depends(get_async_session)
):
    if await UserRepository.get_by_username(session, username=new_user.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    hashed_password = hash_password(new_user.password)

    await UserRepository.insert(
        session, username=new_user.username, hashed_password=hashed_password
    )
    await session.commit()


@router.post("/login", response_model=TokenInfo, tags=["Auth"])
async def login(
    request: Request,
    user: UserResponse = Depends(validate_auth_user),
    session: AsyncSession = Depends(get_async_session),
):
    token_info = await create_user_session(session, user.id, user.username, request)

    await session.commit()

    return token_info


@router.post("/refresh", response_model=TokenInfo, tags=["Auth"])
async def refresh_tokens(
    request: Request,
    body: TokenRefresh,
    session: AsyncSession = Depends(get_async_session),
):
    old_refresh_token = body.refresh_token
    old_refresh_token_hash = hash_refresh_token(old_refresh_token)

    refresh_token = await RefreshTokenRepository.get_by_hash(
        session, old_refresh_token_hash
    )

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if refresh_token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    if refresh_token.expires_at < datetime.now(tz=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired. Please log in again.",
        )

    if refresh_token.is_used:
        await RefreshTokenRepository.revoke_all_user_tokens(
            session, refresh_token.user_id
        )
        await session.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Security breach detected. All sessions revoked.",
        )

    if refresh_token.device_info != request.headers.get("user-agent"):
        refresh_token.is_revoked = True
        await session.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session environment changed. Please log in again.",
        )

    refresh_token.is_used = True

    token_info = await create_user_session(
        session, refresh_token.user_id, refresh_token.user.username, request
    )

    await session.commit()

    return token_info


@router.get("/me", response_model=UserResponse, tags=["Auth"])
async def get_current_user(user: UserResponse = Depends(get_current_auth_user)):
    return user
