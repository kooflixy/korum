from fastapi import APIRouter

from src.frontend.pages import router as pages_router

frontend_router = APIRouter()

frontend_router.include_router(pages_router)
