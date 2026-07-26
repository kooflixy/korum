from fastapi import APIRouter, HTTPException, status

from src.db import async_session_factory
from src.features.auth.repository import UserRepository
from src.features.auth.schemas import UserCreate, UserResponse
from src.features.auth.security import hash_password

router = APIRouter(prefix="/users")


@router.post("/register", status_code=status.HTTP_201_CREATED, tags=['Users'])
async def register(new_user: UserCreate):
    async with async_session_factory() as session:
        if await UserRepository.get_by_username(session, username=new_user.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

        hashed_password = hash_password(new_user.password)

        await UserRepository.insert(
            session, username=new_user.username, hashed_password=hashed_password
        )
        await session.commit()


@router.get("/{user_id}", response_model=UserResponse, tags=['Users'])
async def get_user(user_id: int) -> UserResponse:
    async with async_session_factory() as session:
        user = await UserRepository.get_by_id(session, id=user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user
