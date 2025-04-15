# src/services/sheets.py

from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

sheets_service = build('sheets', 'v4', credentials=credentials)

def append_row(spreadsheet_id, row: list, range="Sheet1!A1"):
    body = {'values': [row]}
    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range,
        valueInputOption="RAW",
        body=body
    ).execute()
    return result