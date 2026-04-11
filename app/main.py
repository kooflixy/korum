from fastapi import FastAPI

from app.config import logging_configure

from app.api import *

logging_configure()

app = FastAPI()

app.include_router(posts.router)