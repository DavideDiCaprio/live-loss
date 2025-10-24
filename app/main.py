from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .routers import feel_lucky_game, users 
from .database import engine, Base, DATABASE_URL, AsyncSessionLocal, get_db
from . import init_db, crud 


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
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Welcome endpoint that renders an HTML page. 
    Now also fetches all users for the leaderboard.
    """
    # Fetch all users (setting a high limit)
    users = await crud.get_users(db, skip=0, limit=1000)
    
    # Sort users by balance, descending
    sorted_users = sorted(users, key=lambda user: user.balance, reverse=True)
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "users": sorted_users}
    )