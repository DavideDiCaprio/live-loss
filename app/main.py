# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import pages, users

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include the routers
app.include_router(pages.router)
app.include_router(users.router)