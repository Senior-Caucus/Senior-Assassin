# src/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException
# from ..auth import get_current_admin  # or your own admin check logic
# get the templates from config
from ..config import templates

router = APIRouter()

@router.get("/dashboard")
def admin_dashboard():
    # maybe fetch data from Google Sheets
    return templates.TemplateResponse("admin_dashboard.html", {"request": {}, "data": {}})

@router.post("/approve-evidence")
def approve_evidence(evidence_id: str):
    # logic to mark an evidence as approved
    return {"message": f"Approved evidence {evidence_id}"}