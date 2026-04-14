from typing import Optional

from fastapi import APIRouter, HTTPException, status

from src.db import async_session_factory
from src.db.models import PostsORM
from src.db.queries import PostsORMHandler
from src.schemas.posts import AddedPostsSchema, PostsGetSchema

router = APIRouter(prefix="/posts")


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
