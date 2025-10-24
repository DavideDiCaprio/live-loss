from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .routers import feel_lucky_game, users 
from .database import engine, Base, DATABASE_URL, AsyncSessionLocal
from . import init_db 


templates = Jinja2Templates(directory="app/templates")

# ---  startup event ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    db_file = "test.db"
    if "sqlite" in DATABASE_URL and db_file in DATABASE_URL:
        if os.path.exists(db_file):
            print(f"Removing old database file: {db_file}")
            os.remove(db_file)
            
    async with engine.begin() as conn:
        print("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("Starting database seeding...")
    await init_db.create_random_users(AsyncSessionLocal, num_users=15)
    
    print("--- Application startup complete. ---")
    yield
    print("--- Application shutting down. ---")
# ------------------------------


app = FastAPI(
    title=os.getenv("APP_TITLE", "Live-Loss API"),
    description=os.getenv("APP_DESCRIPTION", "API for the Live-Loss project."),
    lifespan=lifespan 
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(feel_lucky_game.router) 
app.include_router(users.router) 

@app.get("/")
async def read_root(request: Request):
    """
    Welcome endpoint that renders an HTML page. 
    """
    return templates.TemplateResponse("index.html", {"request": request})
