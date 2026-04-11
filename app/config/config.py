import os
from logging import getLogger

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


settings = Settings()

log.info("Были получены настройки приложения из виртуальной среды")
