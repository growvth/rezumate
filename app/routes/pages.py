from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("pages/score.html", {"request": request, "active_tab": "score"})


@router.get("/score")
async def score_page(request: Request):
    return templates.TemplateResponse("pages/score.html", {"request": request, "active_tab": "score"})


@router.get("/compare")
async def compare_page(request: Request):
    return templates.TemplateResponse("pages/compare.html", {"request": request, "active_tab": "compare"})


@router.get("/rank")
async def rank_page(request: Request):
    return templates.TemplateResponse("pages/rank.html", {"request": request, "active_tab": "rank"})


@router.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse("pages/chat.html", {"request": request, "active_tab": "chat"})
