import os
from logging import getLogger
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

log = getLogger(__name__)

load_dotenv()


class Settings(BaseModel):
    # db
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT"))
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_NAME: str = os.getenv("DB_NAME")

    DATABASE_URL_asyncpg: str = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    DATABASE_URL_psycopg: str = (
        f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    PRIVATE_KEY: str = open("certs/private.pem", "r", encoding="utf-8").read()
    PUBLIC_KEY: str = open("certs/public.pem", "r", encoding="utf-8").read()
    ALGORITHM: str = "RS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    RECORDS_COUNT_ON_PAGE: int = 10


settings = Settings()

log.info("Были получены настройки приложения из виртуальной среды")
