from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api import main_router
from src.config import logging_configure
from src.frontend import frontend_router

logging_configure()

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/frontend/static"), "static")
app.include_router(main_router)
app.include_router(frontend_router)
