# src/routers/admin.py

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response, JSONResponse, RedirectResponse
# get the templates from config
from ..config import templates
from ..services.sheets import scan_sheet, edit_row, USERS_SHEET_ID, EVIDENCE_SHEET_ID
from ..services.drive import download_video_evidence, DRIVE_ASSASSIN_EVIDENCE_FOLDER_ID
from .auth import get_row, SESSIONS_SHEET_ID
import re

router = APIRouter()

@router.get("/dashboard")
def admin_dashboard(request: Request):
    session_id = str(request.cookies.get("session_id"))
    row = get_row(SESSIONS_SHEET_ID, session_id)
    if not row or len(row) < 5 or (row[4] != "TRUE" and row[4] != "True"):
        return RedirectResponse("/test")

    # fetch data from Google Sheets
    user_values = scan_sheet(USERS_SHEET_ID)
    evidence_values = scan_sheet(EVIDENCE_SHEET_ID) # header: evidence_id	assassin	target	evidence_path	evidence_size	approved

    # Get number of alive users
    alive_index = user_values[0].index("alive")
    num_alive_users = sum(1 for row in user_values[1:] if len(row) > alive_index and
                          (row[alive_index] == "True" or row[alive_index] == "TRUE"))

    # Get the number of approved evidence
    approved_index = evidence_values[0].index("approved")
    num_approved_evidence = sum(1 for row in evidence_values[1:] if row[approved_index] == "True" or row[approved_index] == "TRUE")
    num_unapproved_evidence = sum(1 for row in evidence_values[1:] if row[approved_index] == "False" or row[approved_index] == "FALSE")
    num_awaiting_evidence = sum(1 for row in evidence_values[1:] if row[approved_index] == "None" or row[approved_index] == "NONE")

    # For the awaiting evidence, we want to pass it into the template along with the evidence ID, assassin, target, and evidence path
    awaiting_evidence = [
        {
            "evidence_id": row[0],
            "assassin": row[1],
            "target": row[2],
            "evidence_path": row[3],
            "full_evidence_path": row[0] + "." + row[7]
        }
        for row in evidence_values[1:] if row[approved_index] == "None" or row[approved_index] == "NONE"
    ]

    return templates.TemplateResponse("admin_dashboard.html", 
                                      {"request": request,
                                       "num_alive_users": num_alive_users,
                                       "num_approved_evidence": num_approved_evidence,
                                       "num_unapproved_evidence": num_unapproved_evidence,
                                       "num_awaiting_evidence": num_awaiting_evidence,
                                       "awaiting_evidence": awaiting_evidence})

@router.get("/video_evidence/{evidence_id}")
def get_video_evidence(request: Request, evidence_id: str):
    # 1) download entire file into BytesIO
    try:
        video_io = download_video_evidence(
            DRIVE_ASSASSIN_EVIDENCE_FOLDER_ID,
            evidence_id
        )
    except FileNotFoundError:
        raise HTTPException(404, "Evidence not found.")

    data = video_io.getvalue()
    total = len(data)

    # 2) check for Range header
    range_header = request.headers.get("range")
    if range_header:
        # e.g. "bytes=123-"
        m = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if m:
            start = int(m.group(1))
            end = int(m.group(2)) if m.group(2) else total - 1
            if end >= total:
                end = total - 1
            chunk = data[start : end + 1]
            headers = {
                "Content-Range": f"bytes {start}-{end}/{total}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(len(chunk)),
                "Content-Type": "video/mp4",
            }
            return Response(content=chunk, status_code=206, headers=headers)
        # if malformed, fall through to full download

    # 3) no Range → send full
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(total),
    }
    return Response(content=data, media_type="video/mp4", headers=headers)

@router.post("/approve-evidence/{evidence_id}/{approved}")
def approve_evidence(evidence_id: str, approved: bool):
    if not evidence_id:
        raise HTTPException(status_code=400, detail="Evidence ID is required.")

    # Edit the evidence row in the EVIDENCE_SHEET_ID to set approved status
    success = edit_row(
        EVIDENCE_SHEET_ID,
        evidence_id,
        "approved",
        str(approved),
        range="Sheet1!A:Z"
    )
    
    # Let's get some additional information about the evidence
    row = get_row(EVIDENCE_SHEET_ID, evidence_id)
    user_email = str(row[1] if row is not None and len(row) > 1 else None)
    target_email = str(row[2] if row is not None and len(row) > 2 else None)

    if approved:
        # Edit the target's row in the USERS_SHEET_ID to set alive to False
        edit_row(USERS_SHEET_ID, target_email, "alive", "False", range="Sheet1!A:Z")
        # Find the target's target
        target_row = get_row(USERS_SHEET_ID, target_email)
        target_target_email = str(target_row[2] if target_row is not None and len(target_row) > 2 else None)
        # Give the assassin the target's target
        edit_row(USERS_SHEET_ID, user_email, "currentTarget", target_target_email, range="Sheet1!A:Z")
        # Set awaiting to False for the assassin
        edit_row(USERS_SHEET_ID, user_email, "waiting", "False", range="Sheet1!A:Z")
    else:
        # If not approved, we can just set the waiting flag to False
        edit_row(USERS_SHEET_ID, user_email, "waiting", "False", range="Sheet1!A:Z")

    return JSONResponse({"message": "OK"})