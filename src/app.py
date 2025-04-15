# src/app.py

import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routers import admin, user, pages

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

app = FastAPI(title="Senior Assassin", version="0.1.0")

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

# Example root path
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI - root endpoint"}