# src/services/firebase_auth.py

import os
from typing import Tuple, Optional
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException
from src.services.sheets import check_admin

# Initialize Firebase Admin only once.
if not firebase_admin._apps:
    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "src/secrets/firebase_service_account.json")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token: str) -> Tuple[str, Optional[str]]:
    """
    Verifies the Firebase ID token, checks the email domain and '5', 
    and returns a tuple (email, full_name). Raises HTTPException on failure.
    """
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        email = decoded_token.get("email", "")
        uid = decoded_token.get("uid")
        user_record = firebase_auth.get_user(uid)
        full_name = user_record.display_name  # may be None if not set
        admin = check_admin(email)
        if not admin and not (email.endswith("@stuy.edu") and "5" in email):
            raise HTTPException(status_code=403, detail="Email must be @stuy.edu and contain a '5'.")
        return email, full_name, admin
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token.") from e