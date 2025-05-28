from ..services.drive import file_exists, DRIVE_PICTURES_FOLDER_ID
from ..services.sheets import scan_sheet, USERS_SHEET_ID

user_sheet = scan_sheet(USERS_SHEET_ID)
for row in user_sheet[1:]:  # Skip header
    picture_path = row[7].strip() if len(row) > 7 else ""

    # Check if the file exists in Google Drive
    if picture_path and not file_exists(DRIVE_PICTURES_FOLDER_ID, picture_path):
        print(f"User {row[0]} ({row[1]}) has no profile picture: {picture_path}")
    else:
        print(f"User {row[0]} ({row[1]})")