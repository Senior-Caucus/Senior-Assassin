# src/services/sheets.py

from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

USERS_SHEET_ID = '164g6_pWSpecS8DQGR1utIVwAhxNYxBVCbPpyqkcbyD0'
METADATA_SHEET_ID = '1g6Q_G0Mr4yNfs3JlqgR2WEYoPfNRn1xHOTXf'
EVIDENCE_SHEET_ID = '1pO6_1kKZ4orrH7WP666Y3hcrm4rKR09TqGbSuFMDKSA'
SESSIONS_SHEET_ID = '1nqEHT8Udqli3oe_-VuKNHSBIkkNIMEpF7V4aK4pp3kE'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

sheets_service = build('sheets', 'v4', credentials=credentials)

def append_row(spreadsheet_id, row: list, range="Sheet1!A:Z"):
    body = {'values': [row]}
    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range,
        valueInputOption="RAW",
        body=body
    ).execute()
    return result

def exists(spreadsheet_id, pk: str, range="Sheet1!A:Z") -> bool:
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range
    ).execute()
    values = result.get('values', [])
    for value in values:
        if value and value[0] == pk:
            return True
    return False

# Get row by primary key
def get_row(spreadsheet_id, pk: str, range="Sheet1!A:Z"):
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range
    ).execute()
    values = result.get('values', [])
    for value in values:
        if value and value[0] == pk:
            return value
    return None

# Check if a user is admin
def check_admin(email: str) -> bool:
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=USERS_SHEET_ID,
        range="Sheet1!A:Z"
    ).execute()
    values = result.get('values', [])
    for value in values:
        if value and value[0] == email and value[1] == "admin":
            return True
    return False