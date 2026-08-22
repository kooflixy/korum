from datetime import datetime
from typing import Optional

from pydantic import Field

from src.core.schemas import BaseModel
from src.features.users.schemas import UserResponse


class PostCreate(BaseModel):
    title: Optional[str] = Field(min_length=1, max_length=256)
    content: Optional[str] = None


class PostUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=256)
    content: Optional[str] = None


class PostResponse(BaseModel):
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
