from fastapi import APIRouter

router = APIRouter()


@router.get("/post")
async def get_post():
    return "getted post"
