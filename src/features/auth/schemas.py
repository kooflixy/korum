from typing import Annotated

from pydantic import BaseModel, StringConstraints

from src.features.users.schemas import Username

Password = Annotated[str, StringConstraints(min_length=8, max_length=256)]


class UserCreate(BaseModel):
    username: Username
    password: Password
