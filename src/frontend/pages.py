from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML_PATH = "src/frontend/static/html/"


def get_html(path: str):
    path = HTML_PATH + path
    return open(path, "r", encoding="utf-8").read()


@router.get("/", tags=["FRONTEND"])
async def home():
    return HTMLResponse(get_html("home.html"))


@router.get("/register", tags=["FRONTEND"])
async def registration():
    return HTMLResponse(get_html("registration.html"))
