# src/routers/user.py
# router: /user/endpoint

from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
from ..services.drive import upload_video_evidence, DRIVE_ASSASSIN_EVIDENCE_FOLDER_ID
from ..services.sheets import append_row, EVIDENCE_SHEET_ID, edit_row, USERS_SHEET_ID, scan_sheet
import uuid
import time

router = APIRouter()

@router.get("/profile")
def get_user_profile():
    # logic to show user profile, maybe info from Google
    return {"message": "User profile data"}

@router.post("/submit-evidence")
async def submit_evidence(
    request: Request,
    target_email: str = Form(...),
    user_email: str = Form(...),
    video: UploadFile = File(...),
    comments: str = Form("")
):
    # 1) Check if evidence already exists for this user-target pair
    from ..services.sheets import scan_sheet
    evidence_rows = scan_sheet(EVIDENCE_SHEET_ID) or []
    for row in evidence_rows[1:]:
        if len(row) >= 3 and row[1] == user_email and row[2] == target_email:
            return JSONResponse({
                "message": "Evidence already submitted for this user-target pair.",
                "redirect": "/target"
            }, status_code=400)
    # 2) read bytes & enforce 25 MB limit
    data = await video.read()
    size = len(data)
    if size > 25 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 25 MB)")

    # 3) upload to Drive (naming folder “assassin-target”)
    extension = "mp4" if not video.filename else video.filename.split('.')[-1]
    evidence_uuid = str(uuid.uuid4())
    drive_path = evidence_uuid + "." + extension
    _ = upload_video_evidence(
        DRIVE_ASSASSIN_EVIDENCE_FOLDER_ID,
        drive_path,
        data,
        video.content_type or "video/mp4"
    )
    # 4) log in your evidence sheet (no approval needed)
    new_row = [
        evidence_uuid,           # evidence_id
        user_email,    # assassin
        target_email,      # target
        drive_path,        # evidence_path
        str(size),         # evidence_size
        "True",           # approved (auto-approved)
        comments,          # comments
        extension,         # extension
        str(int(time.time())),  # timestamp
    ]
    append_row(EVIDENCE_SHEET_ID, new_row)
    
    # 5) Update hearts for both users
    from ..services.sheets import scan_sheet, edit_row
    user_rows = scan_sheet(USERS_SHEET_ID) or []
    header = user_rows[0] if user_rows else []
    idx = lambda col: header.index(col) if col in header else None
    # Get assassin and target rows
    assassin_row = next((r for r in user_rows[1:] if r and r[0] == user_email), None)
    target_row = next((r for r in user_rows[1:] if r and r[0] == target_email), None)
    if assassin_row and target_row:
        hearts_idx = idx("hearts")
        if hearts_idx is not None:
            # Parse hearts as float, default 0
            try:
                assassin_hearts = float(assassin_row[hearts_idx]) if assassin_row[hearts_idx] else 0.0
            except Exception:
                assassin_hearts = 0.0
            try:
                target_hearts = float(target_row[hearts_idx]) if target_row[hearts_idx] else 0.0
            except Exception:
                target_hearts = 0.0
            # Assassin gain logic
            if assassin_hearts in [0, 1/3, 2/3]:
                assassin_hearts += 1/3
            else:
                assassin_hearts += 1
            # Target loses a heart
            target_hearts = max(0, target_hearts - 1)
            edit_row(USERS_SHEET_ID, user_email, "hearts", str(assassin_hearts))
            edit_row(USERS_SHEET_ID, target_email, "hearts", str(target_hearts))
    # 6) return a redirect to /target
    return JSONResponse({
        "message": "Evidence submitted. Hearts updated.",
        "redirect": "/target"
    })