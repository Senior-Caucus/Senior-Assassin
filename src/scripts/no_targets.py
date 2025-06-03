import sys
from ..services.sheets import scan_sheet, USERS_SHEET_ID

def list_unassigned_alive_users():
    """
    Prints a list of alive users (emails) who are not being targeted by any alive user.
    """
    # Fetch all rows from the Google Sheet
    values = scan_sheet(USERS_SHEET_ID)
    if not values or len(values) < 2:
        print("No data found or not enough rows.")
        return

    # The first row is the header
    header, *all_rows = values

    # Determine the index of each relevant column
    # Expected header order:
    # [email, role, currentTarget, assassinationStatus, createdAt, fullName, waiting, picturePath, schedule, alive, feet, inches]
    try:
        EMAIL_IDX   = header.index("email")
        TARGET_IDX  = header.index("currentTarget")
        ALIVE_IDX   = header.index("alive")
    except ValueError as e:
        print(f"Missing expected column in header: {e}")
        return

    alive_users = set()
    targeted_users = set()

    # First pass: collect all alive users and record whom they target
    for row in all_rows:
        if len(row) <= max(EMAIL_IDX, TARGET_IDX, ALIVE_IDX):
            continue

        email   = row[EMAIL_IDX].strip().lower()
        is_alive = row[ALIVE_IDX].strip().lower() == "true"
        target   = row[TARGET_IDX].strip().lower()

        if is_alive:
            alive_users.add(email)
            if target:
                targeted_users.add(target)

    # Alive users who have no one targeting them
    unassigned = sorted(alive_users - targeted_users)

    # Print results
    if not unassigned:
        print("✅ Every alive user is targeted by at least one alive user.")
    else:
        print("❌ The following alive users have no one targeting them:\n")
        for email in unassigned:
            print(f" - {email}")

if __name__ == "__main__":
    list_unassigned_alive_users()