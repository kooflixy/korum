from fastapi import APIRouter

from src.features.auth.router import router as auth_router
from src.features.posts.router import router as posts_router
from src.features.users.router import router as users_router

main_router = APIRouter(prefix="/api")

main_router.include_router(posts_router)
main_router.include_router(users_router)
main_router.include_router(auth_router)
