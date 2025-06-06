from ..services.sheets import scan_sheet, edit_rows, USERS_SHEET_ID

def eliminate_ppl():
    users = scan_sheet(USERS_SHEET_ID)
    elim_arr = []

    to_keep =  open("./src/scripts/to_keep.txt", "r").read().split('\n')
    print(to_keep)

    header = users[0]
    for user in users[1:]:
        email = user[header.index("email")]
        try:
            isAlive = user[header.index("alive")].lower()
        except:
            isAlive = "false"
        if email not in to_keep and isAlive == "true":
            print(user[header.index("fullName")])

eliminate_ppl()