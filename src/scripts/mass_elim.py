from ..services.sheets import scan_sheet, edit_rows, USERS_SHEET_ID
import string

"""
edit rows funtion in sheets
def edit_rows(spreadsheet_id: str, requests, range="Sheet1!A:Z"):
    
    Edit multiple rows in a Google Sheet using batch update requests.
    Each request should be a dictionary with the necessary parameters.
    
    body = {
        'valueInputOption': 'RAW',
        'data': requests
    }
    
    result = sheets_service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()
    
    return result"""

def eliminate_ppl():
    users = scan_sheet(USERS_SHEET_ID)
    elim_arr = []

    to_keep =  open("./src/scripts/to_keep.txt", "r").read().split('\n')
    print(to_keep)

    header = users[0]
    alive_col_idx = header.index("alive")
    update_requests = []

    for user in users[1:]:
        email = user[header.index("email")]
        try:
            isAlive = user[alive_col_idx].lower()
        except:
            isAlive = "false"
        if email not in to_keep and isAlive == "true":
            row_num = users.index(user) + 1
            col_letter = chr(ord('A') + alive_col_idx)
            update_requests.append({"range": f"Sheet1!{col_letter}{row_num}", "values": [["false"]]})

    if update_requests:
        edit_rows(USERS_SHEET_ID, update_requests)

eliminate_ppl()