from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.config import settings
from src.db import async_session_factory
from src.features.auth.router import get_current_user
from src.features.posts.model import PostORM
from src.features.posts.repository import PostRepository
from src.features.posts.schemas import PostCreate, PostListResponse, PostResponse
from src.features.users.schemas import UserResponse

router = APIRouter(prefix="/posts")


@router.get("/page", response_model=PostListResponse, tags=["Posts"])
async def get_posts_page(
    page: int = 1,
    sort_by: Literal["id"] = "id",
    order_by: Literal["asc", "desc"] = "desc",
) -> PostListResponse:
    async with async_session_factory() as session:
        posts_list = await PostRepository.get_page(
            session, page=page, sort_by=sort_by, order_by=order_by
        )

        if len(posts_list) < settings.RECORDS_COUNT_ON_PAGE:
            is_last_page = True
        else:
            is_last_page = await PostRepository.is_last_page(
                session, page=page, sort_by=sort_by, order_by=order_by
            )

        res = dict(data=posts_list, page=page, is_last_page=is_last_page)

        return res


@router.get("/{post_id}", response_model=PostResponse, tags=["Posts"])
async def get_post(post_id: int) -> PostResponse:
    async with async_session_factory() as session:
        post = await PostRepository.get(session, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        return post


@router.post("/create", status_code=status.HTTP_201_CREATED, tags=["Posts"])
async def create_post(
    new_post: PostCreate, user: UserResponse = Depends(get_current_user)
):
    async with async_session_factory() as session:
        await PostRepository.insert(
            session, title=new_post.title, content=new_post.content, author_id=user.id
        )

        await session.commit()
