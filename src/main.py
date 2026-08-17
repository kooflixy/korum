from fastapi import FastAPI

from src.api.router import main_router
from src.core.config import logging_configure

logging_configure()

app = FastAPI()

app.include_router(main_router)
