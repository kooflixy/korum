from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, status

from src.config import settings
from src.db import async_session_factory
from src.db.models import PostsORM
from src.db.queries import PostsORMHandler
from src.schemas.posts import AddedPostsSchema, PostsGetSchema, PostsPageGetSchema

router = APIRouter(prefix="/posts")


@router.get("/page")
async def get_posts_page(
    page: int = 1,
    sort_by: Literal["id"] = "id",
    order_by: Literal["asc", "desc"] = "desc",
) -> PostsPageGetSchema:
    async with async_session_factory() as session:
        posts_list = await PostsORMHandler.get_page(
            session, page=page, sort_by=sort_by, order_by=order_by
        )

        if len(posts_list) < settings.RECORDS_COUNT_ON_PAGE:
            is_last_page = True
        else:
            is_last_page = await PostsORMHandler.is_last_page(
                session, page=page, sort_by=sort_by, order_by=order_by
            )

        res = dict(data=posts_list, page=page, is_last_page=is_last_page)

        return res


@router.get("/{post_id}")
async def get_post(post_id: int) -> Optional[PostsGetSchema]:
    async with async_session_factory() as session:
        post = await PostsORMHandler.get(session, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        return post


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_post(new_post: AddedPostsSchema):
    async with async_session_factory() as session:
        await PostsORMHandler.insert(
            session, title=new_post.title, content=new_post.content
        )

        await session.commit()
