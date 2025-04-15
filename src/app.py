# src/app.py

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routers import admin, user, pages
from .config import templates

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

import sass  # comes from libsass, NOT pysass

@asynccontextmanager
async def lifespan(app: FastAPI):
    scss_file = os.path.join("src", "static", "scss", "main.scss")
    css_file = os.path.join("src", "static", "css", "main.css")
    os.makedirs(os.path.dirname(css_file), exist_ok=True)

    try:
        compiled_css = sass.compile(filename=scss_file)
        with open(css_file, "w") as f:
            f.write(compiled_css)
        print("SCSS successfully compiled to CSS.")
    except Exception as e:
        print(f"Error compiling SCSS: {e}")

    yield

# Initialize the FastAPI app with lifespan support.
app = FastAPI(lifespan=lifespan, title="Senior Assassin", version="0.1.0")

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Root route
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})