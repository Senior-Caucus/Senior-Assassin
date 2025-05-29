# src/routers/pages.py

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, Response
from fastapi.exceptions import HTTPException
from datetime import datetime
from zoneinfo import ZoneInfo

from ..config import templates
from ..services.sheets import scan_sheet, get_target_info, SESSIONS_SHEET_ID, USERS_SHEET_ID, SAFETY_OBJECT_SHEET_ID
from ..services.drive import download_profile_picture
from ..services.logger import logger
from .auth import check_session

router = APIRouter()

@router.get("/robots.txt", response_class=Response, include_in_schema=False)
async def robots_txt():
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /*\n"
    )
    return Response(content=content, media_type="text/plain")

@router.get("/", response_class=HTMLResponse)
def get_index(request: Request):
    return templates.TemplateResponse("new_index.html", {"request": request})

@router.get("/failure", response_class=HTMLResponse)
def get_index(request: Request):
    return templates.TemplateResponse("failure.html", {"request": request})

@router.get("/test", response_class=HTMLResponse)
def get_new_index(request: Request):
    return RedirectResponse(url="/", status_code=302)

@router.get("/rules", response_class=HTMLResponse)
def get_rules_page(request: Request):
    return templates.TemplateResponse("rules.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
def login(request: Request):
    # 1. Get session_id cookie
    session_id = request.cookies.get("session_id")
    if not session_id:
        return RedirectResponse(url="/test", status_code=302)

    # 2. Load session and user tables
    session_rows = scan_sheet(SESSIONS_SHEET_ID) or []
    user_rows    = scan_sheet(USERS_SHEET_ID)    or []

    # Require at least a header row
    if len(session_rows) < 2:
        logger.error("No sessions found in sheet")
        return RedirectResponse(url="/test", status_code=302)
    if len(user_rows) < 2:
        logger.error("No users found in sheet")
        return RedirectResponse(url="/test", status_code=302)

    # 3. Build lookup maps (skip header)
    sessions_by_id = {row[0]: row for row in session_rows[1:] if row}
    users_by_email = {row[0]: row for row in user_rows[1:] if row}

    # 4. Verify session exists
    session = sessions_by_id.get(session_id)
    if not session:
        return RedirectResponse(url="/failure", status_code=302)

    # 5. Verify user exists
    # session row layout: [session_id, timestamp, email, full_name, admin_flag]
    email = session[2] if len(session) >= 3 else None
    user  = users_by_email.get(email, None)
    if not email or not user:
        return RedirectResponse(url="/failure", status_code=302)

    # 6. Admins go to dashboard
    admin_flag = session[4] if len(session) >= 5 else ""
    if admin_flag.strip().lower() == "true":
        return RedirectResponse(url="/admin/dashboard", status_code=302)

    # 7. Check if eliminated: user[9] = alive flag
    alive_flag = user[9] if len(user) > 9 else ""
    if alive_flag.strip().lower() == "false":
        return RedirectResponse(url="/eliminated", status_code=302)

    # 8. Check if waiting: user[6] = waiting flag
    waiting_flag = user[6] if len(user) > 6 else ""
    if waiting_flag.strip().lower() == "true":
        return RedirectResponse(url="/awaiting", status_code=302)

    # 9. Default: send to active target page
    return RedirectResponse(url="/target", status_code=302)
    

@router.get("/target", response_class=HTMLResponse)
def target_page(request: Request):
    # 1. Get session_id cookie
    session_id = request.cookies.get("session_id")
    session_rows = scan_sheet(SESSIONS_SHEET_ID) or []
    session_valid = False

    for row in session_rows[1:]:
        if row and row[0] == session_id:
            session_valid = True
            break

    if not session_id or not session_valid:
        return templates.TemplateResponse("test.html", {"request": request})
    
    # 2. Get user email from session
    if len(session_rows) < 2:
        logger.error("No sessions found in sheet")
        return templates.TemplateResponse("test.html", {"request": request})
    sessions_by_id = {row[0]: row for row in session_rows[1:] if row}
    session = sessions_by_id.get(session_id)
    if not session or len(session) < 3:
        logger.error("Session not found or invalid format")
        return templates.TemplateResponse("test.html", {"request": request})
    user_email = session[2]
    if not user_email:
        logger.error("User email not found in session")
        return templates.TemplateResponse("test.html", {"request": request})
    
    # 3. Run the get target_info function to get the target info
    target_info = get_target_info(user_email)
    target_email, target_name, target_picture, target_height, target_schedule = target_info

    # 4. Get the day's safety object and the riddle for the next day
    safety_rows = scan_sheet(SAFETY_OBJECT_SHEET_ID) or [] # Date (MM_DD_YYYY)	Object	Hint
    # Get today's date in MM_DD_YYYY format
    today = datetime.now(ZoneInfo("America/New_York")).strftime("%m_%d_%Y")
    today_safety = str(None)
    tmr_hint = str(None)
    for i in range(1, len(safety_rows)):
        row = safety_rows[i]
        if len(row) < 3:
            continue
        date_str, obj, hint = row[0], row[1], row[2]
        if date_str == today:
            today_safety = obj
            tmr_hint = safety_rows[i + 1][2] if i + 1 < len(safety_rows) else str(None)

    return templates.TemplateResponse("target.html", {"request": request,
                                                        "user_email": user_email,
                                                        "target_email": target_email,
                                                        "target_name": target_name,
                                                        "target_picture": target_picture,
                                                        "target_height": target_height,
                                                        "target_schedule": target_schedule,
                                                        "today_safety": today_safety,
                                                        "tmr_hint": tmr_hint})

@router.get("/profile_picture/{email}/{filename}")
def serve_profile_picture(email: str, filename: str):
    if filename != "profile_pic.jpg":
        raise HTTPException(404, "Not found.")
    # decode and download
    email = email.replace("%40", "@")
    img_io = download_profile_picture(email)
    return StreamingResponse(img_io, media_type="image/jpeg")

@router.get("/awaiting", response_class=HTMLResponse)
def get_awaiting_page(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not check_session(session_id):
        return templates.TemplateResponse("test.html", {"request": request})
    return templates.TemplateResponse("awaiting.html", {"request": request})

@router.get("/winner", response_class=HTMLResponse)
def get_winner_page(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not check_session(session_id):
        return templates.TemplateResponse("test.html", {"request": request})
    return templates.TemplateResponse("winner.html", {"request": request})

@router.get("/eliminated", response_class=HTMLResponse)
def get_eliminated_page(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not check_session(session_id):
        return templates.TemplateResponse("test.html", {"request": request})
    return templates.TemplateResponse("eliminated.html", {"request": request})
