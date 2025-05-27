# src/routers/user.py
# router: /user/endpoint

from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
from ..services.drive import upload_video_evidence, DRIVE_ASSASSIN_EVIDENCE_FOLDER_ID
from ..services.sheets import append_row, EVIDENCE_SHEET_ID, edit_row, USERS_SHEET_ID
import uuid

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
    # 1) read bytes & enforce 25 MB limit
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
        evidence_uuid,
        data,
        video.content_type or "video/mp4"
    )

    # 4) log in your evidence sheet
    new_row = [
        evidence_uuid,           # evidence_id
        user_email,    # assassin
        target_email,      # target
        drive_path,        # evidence_path
        str(size),         # evidence_size
        "None",            # approved
        comments,          # comments
        extension          # extension
    ]
    append_row(EVIDENCE_SHEET_ID, new_row)

    # 5) Edit the current user's row in the USERS_SHEET_ID to set waiting to True
    edit_row(USERS_SHEET_ID, user_email, "waiting", "True")

    # 6) return a redirect to /login
    return JSONResponse({
        "message": "Evidence submitted. Awaiting approval.",
        "redirect": "/login"
    })