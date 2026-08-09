from typing import Annotated

from pydantic import BaseModel, StringConstraints

from src.features.users.schemas import Username

Password = Annotated[str, StringConstraints(min_length=8, max_length=256)]


class UserCreate(BaseModel):
    username: Username
    password: Password


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class TokenRefresh(BaseModel):
    refresh_token: str
