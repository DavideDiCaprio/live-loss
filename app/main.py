from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .routers import feel_lucky_game 
import os

templates = Jinja2Templates(directory="app/templates")


app = FastAPI(
    title=os.getenv("APP_TITLE", "Live-Loss API"),
    description=os.getenv("APP_DESCRIPTION", "API for the Live-Loss project.")
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
# ----------------------------

app.include_router(feel_lucky_game.router) 

@app.get("/")
async def read_root(request: Request):
    """
    Welcome endpoint that renders an HTML page. 
    """
    return templates.TemplateResponse("index.html", {"request": request})
