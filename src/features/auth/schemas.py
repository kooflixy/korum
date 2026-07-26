from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints

Username = Annotated[
    str,
    StringConstraints(
        min_length=5, max_length=64, pattern=r"^[a-zA-Z0-9_]+$", strip_whitespace=True
    ),
]

Password = Annotated[str, StringConstraints(min_length=8, max_length=256)]


class UserCreate(BaseModel):
    username: Username
    password: Password


class UserResponse(BaseModel):
    id: int
    username: Username

    created_at: datetime
    updated_at: datetime
