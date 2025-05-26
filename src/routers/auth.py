# src/routers/auth.py

from fastapi import APIRouter, HTTPException, Header, Response
from ..services.firebase_auth import verify_firebase_token
from ..services.sheets import exists, append_row, get_row, SESSIONS_SHEET_ID, USERS_SHEET_ID
import uuid
import time

router = APIRouter()

def signed_up(session_id: str):
    if not session_id:
        return False
    
    # Check if the session ID exists in the Google Sheet
    exists_result = exists(SESSIONS_SHEET_ID, session_id)
    if not exists_result:
        return False
    
    # Get the row corresponding to the session ID
    row = get_row(SESSIONS_SHEET_ID, session_id)
    if not row:
        return False
    
    # Get the user email
    email = row[2]  # Assuming the email is in the third column (index 2)

    # Check if the user is signed up in the USERS_SHEET_ID
    user_exists = exists(USERS_SHEET_ID, email)
    if not user_exists:
        return False
    
    return True


def check_session(session_id: str):
    if not session_id:
        return False
    
    # Check if the session ID exists in the Google Sheet
    exists_result = exists(SESSIONS_SHEET_ID, session_id)
    if not exists_result:
        return False
    
    return True

@router.post("/login/verify")
def login_verify(response: Response, authorization: str = Header(...)):
    """
    Endpoint to verify the Firebase ID token.
    Expects an Authorization header formatted as: "Bearer <token>".
    Creates a session ID for the user and stores it in a cookie.
    Returns the authenticated user's email if verification is successful.
    """
    # Remove "Bearer " prefix if present.
    token = authorization.replace("Bearer ", "")
    email, full_name, admin = verify_firebase_token(token)

    # Generate a unique session ID.
    session_id = str(uuid.uuid4())

    # Get the current timestamp in epoch time format.
    timestamp = int(time.time())

    # the sessions google sheet header: session_id	timestamp	email
    # Append the session ID, timestamp, and email to the sessions Google Sheet.
    append_row(SESSIONS_SHEET_ID, [session_id, timestamp, email, full_name, "TRUE" if admin else "FALSE"])

    # Set the session ID in a cookie with all desired parameters.
    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=3600,
        httponly=True,
        secure=True,
        samesite="strict"
    )

    return {"email": email, "status": "authenticated"}