# src/services/drive.py

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
# import your credentials, etc.

def upload_file_to_drive(filename: str, filepath: str):
    # Example using the Google Drive API
    service = build('drive', 'v3', credentials=...)
    file_metadata = {'name': filename}
    media = MediaFileUpload(filepath, mimetype='image/jpeg')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    return file.get('id')