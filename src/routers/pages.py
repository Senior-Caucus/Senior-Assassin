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

@router.get("/submit-evidence", response_class=HTMLResponse)
def get_submit_evidence_page(request: Request):
    return templates.TemplateResponse("submit_evidence.html", {"request": request})

@router.get("/awaiting-approval", response_class=HTMLResponse)
def get_awaiting_approval_page(request: Request):
    return templates.TemplateResponse("awaiting_approval.html", {"request": request})

@router.get("/winner", response_class=HTMLResponse)
def get_winner_page(request: Request):
    return templates.TemplateResponse("winner.html", {"request": request})