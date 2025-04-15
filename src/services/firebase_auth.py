# src/services/firebase_auth.py
import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException

# Initialize Firebase Admin only once
if not firebase_admin._apps:
    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "src/secrets/firebase_service_account.json")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token: str) -> str:
    """
    Verifies the Firebase ID token and checks the email domain and the presence of '5'.
    Returns the user's email if valid.
    Raises HTTPException if verification fails or if the email does not meet criteria.
    """
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        email = decoded_token.get("email", "")
        if not (email.endswith("@stuy.edu") and "5" in email):
            raise HTTPException(status_code=403, detail="Email must be @stuy.edu and contain a '5'.")
        return email
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token.") from e