from fastapi import APIRouter, HTTPException, status

from src.db import async_session_factory
from src.features.auth.security import hash_password
from src.features.users.repository import UserRepository
from src.features.users.schemas import UserResponse

router = APIRouter(prefix="/users")


@router.get("/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(user_id: int) -> UserResponse:
    async with async_session_factory() as session:
        user = await UserRepository.get_by_id(session, id=user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user
