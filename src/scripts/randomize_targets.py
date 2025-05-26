from ..services.sheets import scan_sheet, edit_row, USERS_SHEET_ID
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

    """for user in users:
        email = user[0]
        target_email = targets[email]
        if target_email:
            success = edit_row(USERS_SHEET_ID, email, "target", target_email)
            if not success:
                print(f"Failed to update target for {email} to {target_email}")
            else:
                print(f"Updated target for {email} to {target_email}")"""

if __name__ == "__main__":
    randomize_targets()