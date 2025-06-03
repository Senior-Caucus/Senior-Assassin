import sys
from ..services.sheets import scan_sheet, USERS_SHEET_ID

def confirm_alive_targets():
    """
    Confirms that every user marked as 'alive' has a currentTarget
    who is also marked as 'alive'. Prints out any inconsistencies.
    """
    # Fetch all rows from the Google Sheet
    values = scan_sheet(USERS_SHEET_ID)
    if not values or len(values) < 2:
        print("No data found or not enough rows.")
        return

    # The first row is the header
    header, *all_rows = values

    # Determine the index of each relevant column based on the provided header
    # Expected header order: 
    # [email, role, currentTarget, assassinationStatus, createdAt, fullName, waiting, picturePath, schedule, alive, feet, inches]
    try:
        EMAIL_IDX          = header.index("email")
        TARGET_IDX         = header.index("currentTarget")
        ALIVE_IDX          = header.index("alive")
    except ValueError as e:
        print(f"Missing expected column in header: {e}")
        return

    # Build a lookup: email -> alive status ("true"/"false")
    email_to_alive = {}
    for row in all_rows:
        # Skip rows that don't have at least enough columns
        if len(row) <= max(EMAIL_IDX, ALIVE_IDX):
            continue
        email = row[EMAIL_IDX].strip().lower()
        alive_flag = row[ALIVE_IDX].strip().lower()
        email_to_alive[email] = (alive_flag == "true")

    # Now, for every row where 'alive' is true, check that their currentTarget exists and is also alive
    invalid_assignments = []
    for row in all_rows:
        # Skip rows lacking required columns
        if len(row) <= max(EMAIL_IDX, TARGET_IDX, ALIVE_IDX):
            continue

        email       = row[EMAIL_IDX].strip().lower()
        is_alive    = row[ALIVE_IDX].strip().lower() == "true"
        target      = row[TARGET_IDX].strip().lower()

        if not is_alive:
            continue  # we only care about users who are marked alive

        if not target:
            invalid_assignments.append(
                (email, "<no target specified>", "No target")
            )
            continue

        target_alive_status = email_to_alive.get(target, None)
        if target_alive_status is None:
            invalid_assignments.append(
                (email, target, "Target not found in sheet")
            )
        elif not target_alive_status:
            invalid_assignments.append(
                (email, target, "Target is marked 'alive' = false")
            )

    # Print out results
    if not invalid_assignments:
        print("✅ All alive users have an alive target.")
    else:
        print("❌ Found inconsistencies for the following users:")
        print("    (email, currentTarget, issue)\n")
        for email, target, issue in invalid_assignments:
            print(f" - {email} → {target}: {issue}")

if __name__ == "__main__":
    confirm_alive_targets()