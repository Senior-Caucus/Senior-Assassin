import sys
from collections import defaultdict
from ..services.sheets import scan_sheet, USERS_SHEET_ID

def confirm_unique_targets():
    """
    Confirms that no two users marked as 'alive' share the same currentTarget.
    Prints out any duplicate assignments.
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

    # Build a mapping: target_email -> list of alive users who have that target
    target_to_owners = defaultdict(list)

    for row in all_rows:
        # Skip rows lacking required columns
        if len(row) <= max(EMAIL_IDX, TARGET_IDX, ALIVE_IDX):
            continue

        user_email = row[EMAIL_IDX].strip().lower()
        is_alive   = row[ALIVE_IDX].strip().lower() == "true"
        target     = row[TARGET_IDX].strip().lower()

        if not is_alive:
            continue  # Only consider users who are alive

        if target:
            target_to_owners[target].append(user_email)

    # Identify duplicates: any target assigned to more than one alive user
    duplicates = {
        tgt: owners
        for tgt, owners in target_to_owners.items()
        if len(owners) > 1
    }

    # Print results
    if not duplicates:
        print("✅ All alive users have unique targets.")
    else:
        print("❌ Duplicate target assignments found:")
        print("    (target_email → [list_of_alive_users_assigned])\n")
        for tgt, owners in duplicates.items():
            print(f" - {tgt} → {owners}")

if __name__ == "__main__":
    confirm_unique_targets()