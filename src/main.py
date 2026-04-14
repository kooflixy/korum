from fastapi import FastAPI

from src.api import main_router
from src.config import logging_configure

logging_configure()

app = FastAPI()

app.include_router(main_router)
