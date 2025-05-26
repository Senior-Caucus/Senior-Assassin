from ..services.sheets import scan_sheet, edit_rows, USERS_SHEET_ID
import random

def randomize_targets():
    values = scan_sheet(USERS_SHEET_ID)
    if not values or len(values) < 2:
        print("Not enough users to randomize targets.")
        return
    
    # Remove the header row
    header = values[0]
    users = values[1:]

    # Remove all users with role = "admin"
    users = [user for user in users if len(user) > 1 and user[1].lower() != "admin"]
    emails = [user[0] for user in users]

    if len(users) < 2:
        print("Not enough users to randomize targets after removing admins.")
        return
    
    # Shuffle the emails
    random.shuffle(emails)

    # Create a mapping of user to their target, making sure no one targets themselves
    targets = {}
    for i in range(len(emails)):
        target_index = (i + 1) % len(emails)  # Ensure the last user targets the first user
        targets[emails[i]] = emails[target_index]

    # Update the Google Sheet with the new targets
    print(targets)

    requests = []
    i = 0
    for value in values:
        email = value[0]
        if email not in targets:
            continue
        target = targets[email]
        row_index = i
        requests.append({
            "range": f"Sheet1!C{row_index+1}",  # C is the 3rd column, +1 for 1-based index
            "values": [[target]]
        })
        i += 1
    edit_rows(USERS_SHEET_ID, requests)
    print("Targets randomized successfully.")

if __name__ == "__main__":
    randomize_targets()