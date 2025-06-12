# src/routers/pages.py

from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, Response, JSONResponse
from fastapi.exceptions import HTTPException
from googleapiclient.errors import HttpError
from datetime import datetime
from zoneinfo import ZoneInfo
import io

from ..config import templates
from ..services.sheets import scan_sheet, get_target_info, SESSIONS_SHEET_ID, USERS_SHEET_ID, EVIDENCE_SHEET_ID
from ..services.drive import _ensure_user_folder, drive_service, upload_file_to_drive_pfp, download_profile_picture
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
def get_failure(request: Request):
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
        return templates.TemplateResponse("new_index.html", {"request": request})

    # 2. Get user email from session
    if len(session_rows) < 2:
        logger.error("No sessions found in sheet")
        return templates.TemplateResponse("new_index.html", {"request": request})
    sessions_by_id = {row[0]: row for row in session_rows[1:] if row}
    session = sessions_by_id.get(session_id)
    if not session or len(session) < 3:
        logger.error("Session not found or invalid format")
        return templates.TemplateResponse("new_index.html", {"request": request})
    user_email = session[2]
    if not user_email:
        logger.error("User email not found in session")
        return templates.TemplateResponse("new_index.html", {"request": request})

    # 3. Get all users and their info
    user_rows = scan_sheet(USERS_SHEET_ID) or []
    if len(user_rows) < 2:
        logger.error("No users found in sheet")
        return templates.TemplateResponse("new_index.html", {"request": request})
    user_header = user_rows[0]
    users = []
    for row in user_rows[1:]:
        if not row or len(row) < len(user_header):
            continue
        user_dict = {col: row[i] if i < len(row) else "" for i, col in enumerate(user_header)}
        # Add picture path
        user_dict["picture"] = f"/profile_picture/{user_dict['email']}/profile_pic.jpg"
        users.append(user_dict)

    # 4. Get all evidence records
    evidence_rows = scan_sheet(EVIDENCE_SHEET_ID) or []
    evidence_header = evidence_rows[0] if evidence_rows else []
    evidence = []
    for row in evidence_rows[1:]:
        if not row or len(row) < len(evidence_header):
            continue
        evidence.append({col: row[i] if i < len(row) else "" for i, col in enumerate(evidence_header)})

    return templates.TemplateResponse("target.html", {
        "request": request,
        "user_email": user_email,
        "users": users,
        "evidence": evidence
    })

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
        return templates.TemplateResponse("new_index.html", {"request": request})
    return templates.TemplateResponse("awaiting.html", {"request": request})

@router.get("/winner", response_class=HTMLResponse)
def get_winner_page(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not check_session(session_id):
        return templates.TemplateResponse("new_index.html", {"request": request})
    return templates.TemplateResponse("winner.html", {"request": request})

@router.get("/eliminated", response_class=HTMLResponse)
def get_eliminated_page(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not check_session(session_id):
        return templates.TemplateResponse("new_index.html", {"request": request})
    return templates.TemplateResponse("eliminated.html", {"request": request})

@router.get("/profile", response_class=HTMLResponse)
def change_profile_picture_endpoint(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not check_session(session_id):
        return templates.TemplateResponse("new_index.html", {"request": request})
    return templates.TemplateResponse("change_profile.html", {"request": request})

@router.post("/upload_new_profile_picture/{email}", response_class=JSONResponse)
async def replace_profile_picture(email: str, file: UploadFile = File(...)):
    # normalize email
    email = email.replace("%40", "@")
    folder_id = _ensure_user_folder(email)

    # 1) delete any existing profile_pic.jpg in that folder
    try:
        # list files named “profile_pic.jpg”
        q = (
            f"name = 'profile_pic.jpg' and "
            f"'{folder_id}' in parents and "
            "mimeType != 'application/vnd.google-apps.folder'"
        )
        resp = drive_service.files().list(q=q, spaces="drive", fields="files(id)").execute()
        for f in resp.get("files", []):
            drive_service.files().delete(fileId=f["id"]).execute()
    except HttpError as e:
        raise HTTPException(500, f"Failed to clean up old pictures: {e}")

    # 2) upload the new one under the same name
    contents = await file.read()
    bio = io.BytesIO(contents)
    bio.name = "profile_pic.jpg"
    try:
        new_file = upload_file_to_drive_pfp(
            name="profile_pic.jpg",
            file_stream=bio,
            mime_type=str(file.content_type),
            parents=[folder_id]
        )
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {e}")

    return JSONResponse({"status": "ok", "fileId": new_file})

@router.get("/get_email", response_class=JSONResponse)
def get_email(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or not check_session(session_id):
        return JSONResponse({"status": "error", "message": "Invalid session"}, status_code=401)

    session_rows = scan_sheet(SESSIONS_SHEET_ID) or []
    sessions_by_id = {row[0]: row for row in session_rows[1:] if row}
    session = sessions_by_id.get(session_id)

    if not session or len(session) < 3:
        return JSONResponse({"status": "error", "message": "Session not found"}, status_code=404)

    user_email = session[2]
    return JSONResponse({"status": "ok", "email": user_email})