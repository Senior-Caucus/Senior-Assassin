from ..services.sheets import scan_sheet, edit_rows, USERS_SHEET_ID
import random

def randomize_targets():
    values = scan_sheet(USERS_SHEET_ID)
    if not values or len(values) < 2:
        print("Not enough users to randomize targets.")
        return

    # Header is row 1
    header, *all_users = values

    # Filter out admins
    users = [row for row in all_users if len(row) > 1 and row[1].strip().lower() != "admin"]
    emails = [row[0] for row in users]

    if len(emails) < 2:
        print("Not enough non-admin users to randomize targets.")
        return

    # Shuffle and assign
    random.shuffle(emails)
    targets = {emails[i]: emails[(i + 1) % len(emails)] for i in range(len(emails))}
    print("Assigning targets:", targets)

    # Build update requests by walking the original all_users list
    requests = []
    # all_users[i] corresponds to sheet row = i+2 (because header is row 1)
    for idx, row in enumerate(all_users, start=2):
        email = row[0]
        if email in targets:
            requests.append({
                "range": f"Sheet1!C{idx}",
                "values": [[ targets[email] ]]
            })

    if requests:
        edit_rows(USERS_SHEET_ID, requests)
        print("Targets randomized successfully.")
    else:
        print("No matching rows to update.")

if __name__ == "__main__":
    randomize_targets()