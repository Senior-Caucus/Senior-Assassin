# src/routers/auth.py

from fastapi import APIRouter, HTTPException, Header, Response
from ..services.firebase_auth import verify_firebase_token
from ..services.sheets import append_row, SESSIONS_SHEET_ID, USERS_SHEET_ID, METADATA_SHEET_ID, EVIDENCE_SHEET_ID
import uuid
import time

router = APIRouter()

@router.post("/login/verify")
def login_verify(authorization: str = Header(...), response: Response = None):
    """
    Endpoint to verify the Firebase ID token.
    Expects an Authorization header formatted as: "Bearer <token>".
    Creates a session ID for the user and stores it in a cookie.
    Returns the authenticated user's email if verification is successful.
    """
    # Remove "Bearer " prefix if present.
    token = authorization.replace("Bearer ", "")
    email = verify_firebase_token(token)

    # Generate a unique session ID.
    session_id = str(uuid.uuid4())

    # Get the current timestamp in epoch time format.
    timestamp = int(time.time())

    # the sessions google sheet header: session_id	timestamp	email
    # Append the session ID, timestamp, and email to the sessions Google Sheet.
    append_row(SESSIONS_SHEET_ID, [session_id, timestamp, email])

    # Set the session ID in a cookie with all desired parameters.
    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=3600,
        httponly=True,
        secure=True,
        samesite="Strict"
    )

    return {"email": email, "status": "authenticated"}