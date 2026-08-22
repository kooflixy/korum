from src.core.schemas import BaseModel
from src.core.types import Password
from src.features.users.schemas import Username


class UserCreate(BaseModel):
    username: Username
    password: Password


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class TokenRefresh(BaseModel):
    refresh_token: str
