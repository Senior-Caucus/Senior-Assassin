# src/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
# from ..auth import get_current_admin  # or your own admin check logic
# get the templates from config
from ..config import templates
from ..services.sheets import scan_sheet, edit_row, USERS_SHEET_ID, EVIDENCE_SHEET_ID
from ..services.drive import download_video_evidence, DRIVE_ASSASSIN_EVIDENCE_FOLDER_ID

router = APIRouter()

@router.get("/dashboard")
def admin_dashboard(request: Request):
    # fetch data from Google Sheets
    user_values = scan_sheet(USERS_SHEET_ID)
    evidence_values = scan_sheet(EVIDENCE_SHEET_ID) # header: evidence_id	assassin	target	evidence_path	evidence_size	approved

    # Get number of alive users
    alive_index = user_values[0].index("Alive")
    num_alive_users = sum(1 for row in user_values[1:] if row[alive_index] == "True" or row[alive_index] == "TRUE")

    # Get the number of approved evidence
    approved_index = evidence_values[0].index("Approved")
    num_approved_evidence = sum(1 for row in evidence_values[1:] if row[approved_index] == "True" or row[approved_index] == "TRUE")
    num_unapproved_evidence = sum(1 for row in evidence_values[1:] if row[approved_index] == "False" or row[approved_index] == "FALSE")
    num_awaiting_evidence = sum(1 for row in evidence_values[1:] if row[approved_index] == "None" or row[approved_index] == "NONE")

    # For the awaiting evidence, we want to pass it into the template along with the evidence ID, assassin, target, and evidence path
    awaiting_evidence = [
        {
            "evidence_id": row[0],
            "assassin": row[1],
            "target": row[2],
            "evidence_path": row[3]
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
def get_video_evidence(evidence_id: str):
    try:
        video_io = download_video_evidence(
            DRIVE_ASSASSIN_EVIDENCE_FOLDER_ID,
            f"{evidence_id}.mp4"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    return StreamingResponse(video_io, media_type="video/mp4")


@router.post("/approve-evidence/{evidence_id}/{approved}")
def approve_evidence(evidence_id: str, approved: bool):
    if not evidence_id:
        raise HTTPException(status_code=400, detail="Evidence ID is required.")

    success = edit_row(
        EVIDENCE_SHEET_ID,
        evidence_id,
        "approved",
        str(approved),
        range="Sheet1!A:Z"
    )
    if not success:
        raise HTTPException(status_code=404, detail="Evidence ID not found.")
    return JSONResponse({"message": "OK"})