from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2 import service_account
import os
import io
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
SCOPES = ['https://www.googleapis.com/auth/drive.file']

DRIVE_PICTURES_FOLDER_ID = "18sKMfco_KxnmN6hHJVoWcwlBL79mUjXo"
DRIVE_ASSASSIN_EVIDENCE_FOLDER_ID = "1I0s_Xm_Cp2SlxIYsi-GyAl3Bccsl799r"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

drive_service = build('drive', 'v3', credentials=credentials)

def upload_file_to_drive(name, filepath, mime_type, parents=None):
    file_metadata = {'name': name}
    if parents:
        file_metadata['parents'] = parents
    media = MediaFileUpload(filepath, mimetype=mime_type)
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    return file.get('id')

def _ensure_user_folder(email: str) -> str:
    """Find or create a Drive folder named after the user's email."""
    parent_id = DRIVE_PICTURES_FOLDER_ID
    query = (
        f"name = '{email}' and mimeType = 'application/vnd.google-apps.folder' "
        f"and '{parent_id}' in parents"
    )
    res = drive_service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    files = res.get('files', [])
    if files:
        return files[0]['id']
    folder_meta = {
        'name': email,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = drive_service.files().create(body=folder_meta, fields='id').execute()
    return folder.get('id')

def upload_profile_picture(email: str, filepath: str, mime_type: str) -> str:
    """
    Upload a profile picture to the user's Drive folder.
    Returns the uploaded file ID.
    """
    folder_id = _ensure_user_folder(email)
    return upload_file_to_drive("profile_pic.jpg", filepath, mime_type, parents=[folder_id])

def download_profile_picture(email: str) -> str:
    """
    Download the profile picture from the user's Drive folder.
    Returns the file ID of the downloaded picture.
    """
    folder_id = _ensure_user_folder(email)
    query = (
        f"name = 'profile_pic.jpg' and mimeType != 'application/vnd.google-apps.folder' "
        f"and '{folder_id}' in parents"
    )
    res = drive_service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    files = res.get('files', [])
    if not files:
        raise FileNotFoundError("Profile picture not found.")
    return files[0]['id']

def download_video_evidence(folder: str, evidence_path: str) -> io.BytesIO:
    """
    Download video evidence from the specified folder into a BytesIO,
    ready to stream out of a StreamingResponse.
    """
    query = (
        f"name = '{evidence_path}' and mimeType != 'application/vnd.google-apps.folder' "
        f"and '{folder}' in parents"
    )
    res = drive_service.files().list(
        q=query, spaces='drive', fields='files(id)'
    ).execute()
    files = res.get('files', [])
    if not files:
        raise FileNotFoundError("Video evidence not found.")
    file_id = files[0]['id']

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh