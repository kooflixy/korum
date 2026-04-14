from fastapi import APIRouter

from src.api.posts import router as posts_router

main_router = APIRouter(prefix="/api")

main_router.include_router(posts_router)
