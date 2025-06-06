from ..services.sheets import scan_sheet, edit_rows, USERS_SHEET_ID

def eliminate_ppl():
    users = scan_sheet(USERS_SHEET_ID)
    elim_arr = []

    with open("to_keep.txt", "r") as f:
        to_keep = f.readlines()

    header = users[0]
    for user in users[1:]:
        email = user[header.index("email")]
        if email not in to_keep:
            print(email)

if __name__ == "main":
    eliminate_ppl()