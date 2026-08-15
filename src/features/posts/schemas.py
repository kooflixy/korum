from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.features.users.schemas import UserResponse


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    content: Optional[str]


class PostResponse(PostCreate):
    id: int

    title: str = Field(min_length=1, max_length=256)
    content: Optional[str]

    author: UserResponse

    updated_at: datetime
    created_at: datetime


class PostListResponse(BaseModel):
    data: list[PostResponse]

    page: int
    is_last_page: bool
