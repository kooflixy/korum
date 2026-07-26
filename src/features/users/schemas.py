from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints

Username = Annotated[
    str,
    StringConstraints(
        min_length=5, max_length=64, pattern=r"^[a-zA-Z0-9_]+$", strip_whitespace=True
    ),
]


class UserResponse(BaseModel):
    id: int
    username: Username

    created_at: datetime
    updated_at: datetime
