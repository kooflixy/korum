from datetime import datetime

from src.core.schemas import BaseModel
from src.core.types import Username


class UserResponse(BaseModel):
    id: int
    username: Username

    created_at: datetime
    updated_at: datetime
