from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AddedPostsSchema(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    content: Optional[str]


class PostsGetSchema(AddedPostsSchema):
    id: int

    updated_at: datetime
    created_at: datetime


class PostsPageGetSchema(BaseModel):
    data: list[PostsGetSchema]

    page: int
    is_last_page: bool
