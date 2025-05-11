import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .routers import admin, user, pages, auth
from .config import templates
from .services.sheets import get_row, append_row, SESSIONS_SHEET_ID, USERS_SHEET_ID
from .services.drive import upload_profile_picture

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

import sass 
import glob

@asynccontextmanager
async def lifespan(app: FastAPI):
    scss_dir = os.path.join("src", "static", "scss")
    css_dir = os.path.join("src", "static", "css")
    os.makedirs(css_dir, exist_ok=True)

    # Compile SCSS files to CSS
    for scss_file in glob.glob(os.path.join(scss_dir, "*.scss")):
        css_file = os.path.join(css_dir, os.path.basename(scss_file).replace(".scss", ".css"))
        try:
            compiled_css = sass.compile(filename=scss_file)
            with open(css_file, "w") as f:
                f.write(compiled_css)
        except Exception as e:
            print(f"Error compiling {scss_file}: {e}")

    yield

# Initialize the FastAPI app with lifespan support.
app = FastAPI(lifespan=lifespan, title="Senior Assassin", version="0.1.0")

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Include authentication routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Root route
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Post signup route
@app.post("/signup")
async def signup(request: Request, profilePic: UploadFile = File(...)):
    # Parse the incoming form data
    form = await request.form()
    
    # Retrieve the session id from cookies (assumes a cookie named 'session_id')
    session_id = request.cookies.get("session_id")
    if not session_id:
        return {"error": "No session found."}
    
    # Retrieve session row using the session id as primary key
    session_row = get_row(SESSIONS_SHEET_ID, session_id)
    if not session_row:
        return {"error": "Session not found."}

    # Extract email from the session row (assuming email is the second column)
    email = session_row[2] if len(session_row) > 2 else None
    if not email:
        return {"error": "Email not found in session."}
    full_name = session_row[3] if len(session_row) > 3 else None
    if not full_name:
        full_name = "None"

    # Build the schedule list for periods 1-10
    # For each period, if the checkbox is checked then it's considered no class (set as "None"),
    # otherwise use the entered room number (or "None" if left blank)
    schedule_list = []
    for period in range(1, 11):
        room = form.get(f"period{period}_room")
        noclass = form.get(f"period{period}_noclass")
        if noclass:
            schedule_list.append("None")
        else:
            schedule_list.append(room.strip() if room and room.strip() != "" else "None")
    
    # Convert the schedule list to a comma separated string
    schedule_str = ",".join(schedule_list)

    # Construct the new user row using the header:
    # email, role, currentTarget, eliminationHistory, createdAt, fullName, waiting, picturePath, schedule
    import time
    new_user_row = [
        email,            # email from the session
        "user",         # default role is user
        "None",         # currentTarget
        "None",         # eliminationHistory
        str(round(time.time())), # createdAt
        full_name,        # fullName
        "False",        # waiting (not waiting for anything upon signup)
        f"{email}/profile_pic.jpg",         # picturePath (to be handled later)
        schedule_str,    # schedule as a comma separated string,
        "True"          # alive
    ]

    # Check if the user already exists in the USERS_SHEET_ID
    user_exists = get_row(USERS_SHEET_ID, email)
    if user_exists:
        return {"error": "User already exists."}
    
    # Append the new user row to the USERS_SHEET_ID
    append_row(USERS_SHEET_ID, new_user_row)

    # Save profile picture to Drive
    temp_path = f"/tmp/{email}_profile_pic.jpg"
    with open(temp_path, "wb") as f:
        f.write(await profilePic.read())

    _ = upload_profile_picture(email, temp_path, profilePic.content_type)

    os.remove(temp_path)

    return RedirectResponse(url="/success", status_code=303)