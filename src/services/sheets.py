# src/services/sheets.py

from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from .drive import download_profile_picture
from .logger import logger
import io

load_dotenv(dotenv_path=".env.local")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

USERS_SHEET_ID = '164g6_pWSpecS8DQGR1utIVwAhxNYxBVCbPpyqkcbyD0' #   email	role	currentTarget	assassinationStatus	createdAt	fullName	waiting	picturePath	schedule	alive	feet	inches
METADATA_SHEET_ID = '1g6Q_G0Mr4yNfs3JlqgR2WEYoPfNRn1xHOTXf'
EVIDENCE_SHEET_ID = '1pO6_1kKZ4orrH7WP666Y3hcrm4rKR09TqGbSuFMDKSA'
SESSIONS_SHEET_ID = '1nqEHT8Udqli3oe_-VuKNHSBIkkNIMEpF7V4aK4pp3kE'
SAFETY_OBJECT_SHEET_ID = '1RrsEqn9lmDuCC5JDQZI3cDxN5ojCZ4rEZu1cGxBuz_U'

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

# Edit a specific attribute on a row by primary key (using the header to find the column index)
def edit_row(spreadsheet_id, pk: str, attribute: str, value: str, range="Sheet1!A:Z"):
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range
    ).execute()
    values = result.get('values', [])
    
    header = values[0] if values else []
    if not header:
        return False  # No header found
    
    if pk not in [row[0] for row in values]:
        return False  # Primary key not found
    
    row_index = next((i for i, row in enumerate(values) if row and row[0] == pk), None)
    if row_index is None:
        return False  # Row with primary key not found
    
    col_index = header.index(attribute) if attribute in header else None
    if col_index is None:
        return False  # Attribute not found in header
    
    # Update the value
    values[row_index][col_index] = value
    
    body = {'values': values}
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range,
        valueInputOption="RAW",
        body=body
    ).execute()
    
    return True

def edit_rows(spreadsheet_id: str, requests, range="Sheet1!A:Z"):
    """
    Edit multiple rows in a Google Sheet using batch update requests.
    Each request should be a dictionary with the necessary parameters.
    """
    body = {
        'valueInputOption': 'RAW',
        'data': requests
    }
    
    result = sheets_service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()
    
    return result

def scan_sheet(spreadsheet_id: str, range="Sheet1!A:Z"):
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range
    ).execute()
    values = result.get('values', [])
    return values

def get_target_info(user_email: str) -> List[Optional[Any]]:
    """
    Returns [target_email, target_name, picture_url, height_str, schedule_str]
    or [None, None, None, None, None] on any failure.
    """
    # Default “empty” return
    empty: List[Optional[Any]] = [None, None, None, None, None]

    # 1) load the USERS sheet
    rows = scan_sheet(USERS_SHEET_ID) or []
    if len(rows) < 2:
        return empty

    header, *data = rows

    # build a lookup of column → index
    col_idx = {col: idx for idx, col in enumerate(header)}

    # required columns
    def idx(col: str) -> Optional[int]:
        return col_idx.get(col)

    # 2) find the requesting user’s row
    user_row = next((r for r in data if r and r[0] == user_email), None)
    if not user_row:
        return empty

    # 3) get their currentTarget
    t_idx = idx("currentTarget")
    if t_idx is None or t_idx >= len(user_row):
        return empty
    target_email = user_row[t_idx].strip() or None
    if not target_email:
        return empty

    # 4) find the target’s row
    target_row = next((r for r in data if r and r[0] == target_email), None)
    if not target_row:
        return empty

    # 5) pull out the desired fields safely
    # name
    name = None
    name_i = idx("fullName")
    if name_i is not None and name_i < len(target_row):
        name = target_row[name_i].strip() or None

    # schedule
    schedule = None
    sched_i = idx("schedule")
    if sched_i is not None and sched_i < len(target_row):
        schedule = target_row[sched_i].strip() or None
        schedule = schedule.split(",") if schedule else []
    if schedule:
        schedule = {
            f"Period {i+1}": room.strip() if room.strip() else "None"
            for i, room in enumerate(schedule)
        }

    # height
    height = None
    feet_i = idx("feet")
    inches_i = idx("inches")
    if feet_i is not None and inches_i is not None:
        if feet_i < len(target_row) and inches_i < len(target_row):
            ft = target_row[feet_i].strip()
            inch = target_row[inches_i].strip()
            if ft.isdigit() and inch.isdigit():
                height = f"{ft}'{inch}\""

    # picture
    picture = f"/profile_picture/{target_email}/profile_pic.jpg"

    return [target_email, name, picture, height, schedule]