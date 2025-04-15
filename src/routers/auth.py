# src/auth.py

from fastapi import APIRouter, HTTPException, Header
from ..services.firebase_auth import verify_firebase_token

router = APIRouter()

@router.post("/login/verify")
def login_verify(authorization: str = Header(...)):
    """
    Endpoint to verify the Firebase ID token.
    Expects an Authorization header formatted as: "Bearer <token>".
    Returns the authenticated user's email if verification is successful.
    """
    # Remove "Bearer " prefix if present.
    token = authorization.replace("Bearer ", "")
    email = verify_firebase_token(token)
    return {"email": email, "status": "authenticated"}