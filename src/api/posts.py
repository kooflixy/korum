from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, status

from src.config import settings
from src.db import async_session_factory
from src.db.models import PostORM
from src.db.repositories import PostRepository
from src.schemas.post import PostCreate, PostListResponse, PostResponse

router = APIRouter(prefix="/posts")


@router.get("/page")
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


@router.get("/{post_id}")
async def get_post(post_id: int) -> Optional[PostResponse]:
    async with async_session_factory() as session:
        post = await PostRepository.get(session, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        return post


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_post(new_post: PostResponse):
    async with async_session_factory() as session:
        await PostRepository.insert(
            session, title=new_post.title, content=new_post.content
        )

        await session.commit()
