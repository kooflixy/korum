from datetime import datetime
from typing import Optional

from pydantic import computed_field

from src.core.config import settings
from src.core.schemas import BaseModel
from src.core.types import Username


class UserResponse(BaseModel):
    id: int
    username: Username

    avatar_key: Optional[str]

    @computed_field
    def avatar_url(self) -> str:
        avatar_key = self.avatar_key or settings.DEFAULT_AVATAR_KEY
        return f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET}/{avatar_key}"

    created_at: datetime
    updated_at: datetime
