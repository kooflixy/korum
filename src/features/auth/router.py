from fastapi import APIRouter, Depends, HTTPException, status

from src.db import async_session_factory
from src.features.auth.schemas import TokenInfo, UserCreate
from src.features.auth.security import encode_jwt, hash_password
from src.features.auth.service import get_current_auth_user, validate_auth_user
from src.features.users.repository import UserRepository
from src.features.users.schemas import UserResponse

router = APIRouter(prefix="/auth")


@router.post("/register", status_code=status.HTTP_201_CREATED, tags=["Auth"])
async def register(new_user: UserCreate):
    async with async_session_factory() as session:
        if await UserRepository.get_by_username(session, username=new_user.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

        hashed_password = hash_password(new_user.password)

        await UserRepository.insert(
            session, username=new_user.username, hashed_password=hashed_password
        )
        await session.commit()


@router.post("/login", response_model=TokenInfo, tags=["Auth"])
async def login(user: UserResponse = Depends(validate_auth_user)):
    jwt_payload = {"sub": str(user.id), "username": user.username}
    token = encode_jwt(jwt_payload)
    return TokenInfo(access_token=token, token_type="Bearer")


@router.get("/me", response_model=UserResponse, tags=["Auth"])
async def get_current_user(user: UserResponse = Depends(get_current_auth_user)):
    return user
