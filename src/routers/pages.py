# src/routers/pages.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..config import templates
from ..services.sheets import get_row, SESSIONS_SHEET_ID
from .auth import check_session, signed_up

router = APIRouter()

@router.get("/index", response_class=HTMLResponse)
def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login-page", response_class=HTMLResponse)
def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
def target_page(request: Request):
    verified = check_session(request.cookies.get("session_id"))
    if not verified:
        return templates.TemplateResponse("index.html", {"request": request})
    
    # If the user is already signed up, redirect to the target page
    is_signed_up = signed_up(request.cookies.get("session_id"))
    if is_signed_up:
        # We need to check if the user is an admin
        row = get_row(SESSIONS_SHEET_ID, request.cookies.get("session_id"))
        print(row)
        if row and len(row) >= 5 and row[4] == "TRUE":
            return RedirectResponse(url="/admin/dashboard", status_code=302)
        else:
            return RedirectResponse(url="/target", status_code=302)

    return templates.TemplateResponse("signup.html", {"request": request})

@router.get("/target", response_class=HTMLResponse)
def target_page(request: Request):
    verified = check_session(request.cookies.get("session_id"))
    if not verified:
        return templates.TemplateResponse("index.html", {"request": request})
    return templates.TemplateResponse("target.html", {"request": request})

@router.get("/awaiting", response_class=HTMLResponse)
def get_awaiting_page(request: Request):
    verified = check_session(request.cookies.get("session_id"))
    if not verified:
        return templates.TemplateResponse("index.html", {"request": request})
    return templates.TemplateResponse("awaiting.html", {"request": request})

@router.get("/winner", response_class=HTMLResponse)
def get_winner_page(request: Request):
    verified = check_session(request.cookies.get("session_id"))
    if not verified:
        return templates.TemplateResponse("index.html", {"request": request})
    return templates.TemplateResponse("winner.html", {"request": request})