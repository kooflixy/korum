from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db import get_async_session
from src.features.auth.router import get_current_user
from src.features.posts.model import PostORM
from src.features.posts.repository import PostRepository
from src.features.posts.schemas import (
    PostCreate,
    PostListResponse,
    PostResponse,
    PostUpdate,
)
from src.features.users.schemas import UserResponse

router = APIRouter(prefix="/posts")


@router.get("/page", response_model=PostListResponse, tags=["Posts"])
async def get_posts_page(
    page: int = 1,
    sort_by: Literal["id"] = "id",
    order_by: Literal["asc", "desc"] = "desc",
    session: AsyncSession = Depends(get_async_session),
) -> PostListResponse:
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
async def get_post(
    post_id: int, session: AsyncSession = Depends(get_async_session)
) -> PostResponse:
    post = await PostRepository.get(session, post_id)
    if not post or post.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден"
        )
    return post


@router.patch("/{post_id}", response_model=PostResponse, tags=["Posts"])
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> PostResponse:
    post = await PostRepository.get(session, post_id)

    if not post or post.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден"
        )

    if post.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы пытаетесь изменить пост, автором которого не являетесь",
        )

    updated_post = await PostRepository.update(
        session, post_id=post_id, update_data=post_data
    )

    await session.commit()

    return updated_post


@router.post("/create", status_code=status.HTTP_201_CREATED, tags=["Posts"])
async def create_post(
    new_post: PostCreate,
    user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    await PostRepository.insert(
        session, title=new_post.title, content=new_post.content, author_id=user.id
    )

    await session.commit()


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Posts"])
async def delete_post(
    post_id: int,
    user: UserResponse = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    post = await PostRepository.get(session, post_id)

    if not post or post.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден"
        )

    if post.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы пытаетесь удалить пост, автором которого не являетесь",
        )

    await PostRepository.delete_object(session, post)

    await session.commit()
