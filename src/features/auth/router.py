from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_async_session
from src.features.auth.repository import RefreshTokenRepository
from src.features.auth.schemas import (
    TokenInfo,
    TokenRefresh,
    UserCreate,
    UserPasswordUpdate,
    UserUpdate,
)
from src.features.auth.security import (
    hash_password,
    hash_refresh_token,
    validate_password,
)
from src.features.auth.service import (
    create_user_session,
    get_current_auth_user,
    validate_auth_user,
)
from src.features.users.repository import UserRepository
from src.features.users.schemas import UserResponse

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    tags=["Auth"],
)
async def register(
    new_user: UserCreate, session: AsyncSession = Depends(get_async_session)
):
    if await UserRepository.get_by_username(session, username=new_user.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким именем пользователя уже существует",
        )

    hashed_password = hash_password(new_user.password)

    user = await UserRepository.insert(
        session, username=new_user.username, hashed_password=hashed_password
    )
    await session.commit()

    return user


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
            detail="Сессия не найдена",
        )

    if refresh_token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сессия принудительно завершена",
        )

    if refresh_token.expires_at < datetime.now(tz=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сессия истекла. Пожалуйста, войдите заново",
        )

    if refresh_token.is_used:
        await RefreshTokenRepository.revoke_all_user_tokens(
            session, refresh_token.user_id
        )
        await session.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Данный токен уже использовался. В целях безопасности войдите заново",
        )

    if refresh_token.device_info != request.headers.get("user-agent"):
        refresh_token.is_revoked = True
        await session.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Параметры среды изменились. Пожалуйста, войдите заново",
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


@router.patch("/me", response_model=UserResponse, tags=["Auth"])
async def change_user(
    update_data: UserUpdate,
    user: UserResponse = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_async_session),
):
    updated_user = await UserRepository.update(session, user.id, update_data)

    await session.commit()
    return updated_user


@router.post("/change-password", response_model=UserResponse, tags=["Auth"])
async def change_user_password(
    update_data: UserPasswordUpdate,
    user: UserResponse = Depends(get_current_auth_user),
    session: AsyncSession = Depends(get_async_session),
):
    new_password_is_current_exc = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Ваш новый пароль совпадает с текущим",
    )

    if update_data.password == update_data.new_password:
        raise new_password_is_current_exc

    user_record = await validate_auth_user(user.username, update_data.password, session)

    if validate_password(update_data.new_password, user_record.hashed_password):
        raise new_password_is_current_exc

    updated_user = await UserRepository.update(
        session, user.id, {"hashed_password": hash_password(update_data.new_password)}
    )

    await session.commit()

    return updated_user
