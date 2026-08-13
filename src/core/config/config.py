from logging import getLogger

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

log = getLogger(__name__)

load_dotenv()


class Settings(BaseSettings):
    # db
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    MODE: str

    # jwt
    PRIVATE_KEY: str = open("certs/private.pem", "r", encoding="utf-8").read()
    PUBLIC_KEY: str = open("certs/public.pem", "r", encoding="utf-8").read()
    ALGORITHM: str = "RS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # other
    RECORDS_COUNT_ON_PAGE: int = 10


settings = Settings()

log.info("Были получены настройки приложения из виртуальной среды")
