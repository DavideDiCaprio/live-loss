from fastapi import FastAPI
from .routers import items
import os


app = FastAPI(
    title=os.getenv("APP_TITLE", "Live-Loss API"),
    description=os.getenv("APP_DESCRIPTION", "API for the Live-Loss project.")
)

app.include_router(items.router)

@app.get("/")
async def read_root():
    """
    welcame endpoint
    """
    return {"message": "Welcome"}
