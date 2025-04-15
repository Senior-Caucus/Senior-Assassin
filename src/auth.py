# src/auth.py

import os
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/oauth/callback"  # adjust as needed

# We might store the Flow globally or create a function to build it each time
oauth_flow = Flow.from_client_config(
    {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    scopes=[
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
        # Add scopes for Drive or Sheets as needed
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/spreadsheets"
    ]
)

oauth_flow.redirect_uri = REDIRECT_URI

@router.get("/login")
def login_with_google():
    authorization_url, state = oauth_flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return RedirectResponse(authorization_url)

@router.get("/oauth/callback")
def oauth_callback(request: Request, state: Optional[str] = None):
    # Pass state into the flow so that it can verify
    oauth_flow.fetch_token(authorization_response=str(request.url))

    if not oauth_flow.credentials:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token_request = requests.Request()
    id_info = id_token.verify_oauth2_token(
        oauth_flow.credentials.id_token,
        token_request,
        GOOGLE_CLIENT_ID
    )
    user_email = id_info.get("email", "")

    # Restrict to stuy.edu AND must have '5'
    if not (user_email.endswith("@stuy.edu") and '5' in user_email):
        raise HTTPException(status_code=403, detail="Invalid email domain or missing '5'")

    # At this point, user is authenticated
    # You can store user info in session or issue a JWT token
    # Example: 
    # request.session["user"] = user_email

    return RedirectResponse(url="/protected")  # or wherever you want to direct them