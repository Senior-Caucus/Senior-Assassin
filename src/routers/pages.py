# src/routers/pages.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..config import templates

router = APIRouter()

@router.get("/index", response_class=HTMLResponse)
def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login-page", response_class=HTMLResponse)
def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/target", response_class=HTMLResponse)
def target_page(request: Request):
    return templates.TemplateResponse("target.html", {"request": request})

@router.get("/awaiting", response_class=HTMLResponse)
def get_awaiting_page(request: Request):
    return templates.TemplateResponse("awaiting.html", {"request": request})

@router.get("/winner", response_class=HTMLResponse)
def get_winner_page(request: Request):
    return templates.TemplateResponse("winner.html", {"request": request})