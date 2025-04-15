# src/app.py

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from .routers import admin, user, pages, auth
from .config import templates

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