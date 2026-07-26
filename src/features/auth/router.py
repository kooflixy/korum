from fastapi import APIRouter, HTTPException, status

from src.db import async_session_factory
from src.features.auth.schemas import UserCreate
from src.features.auth.security import hash_password
from src.features.users.repository import UserRepository

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
