# src/routers/pages.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..config import templates
from ..services.sheets import scan_sheet, get_row, SESSIONS_SHEET_ID
from .auth import check_session, signed_up

router = APIRouter()

@router.get("/index", response_class=HTMLResponse)
def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/test", response_class=HTMLResponse)
def get_new_index(request: Request):
    return templates.TemplateResponse("new_index.html", {"request": request})

@router.get("/rules", response_class=HTMLResponse)
def get_rules_page(request: Request):
    return templates.TemplateResponse("rules.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
def login(request: Request):
    session_id = str(request.cookies.get("session_id"))
    session_table = scan_sheet(SESSIONS_SHEET_ID)

    verified = True if session_id in [row[0] for row in session_table[1:]] else False
    in_users = get_row(SESSIONS_SHEET_ID, session_id)
    if not verified or not in_users: 
        return RedirectResponse(url="/test", status_code=302)
    
    # Get the session row from the scan
    row = None
    for r in session_table[1:]:
        if r[0] == session_id:
            row = r
            print("Found session row:", row)
            break

    if row and len(row) >= 5 and row[4] == "TRUE":
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    else:
        return RedirectResponse(url="/target", status_code=302)
    

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