from ..services.drive import pfp_exists
from ..services.sheets import scan_sheet, USERS_SHEET_ID

user_sheet = scan_sheet(USERS_SHEET_ID)
for row in user_sheet[1:]:  # Skip header
    email = row[0].strip() if len(row) > 0 else "Unknown"

    # Check if the file exists in Google Drive
    if email and not pfp_exists(email):
        print(f"User {email} has no profile picture")