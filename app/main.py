from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from app import init_db
from app import services
from app.settings import settings 
from app.routers import feel_lucky_game, users
from app.routers import realtime
from app.database import AsyncSessionLocal, get_db


templates = Jinja2Templates(directory="app/templates")

# --- LIFESPAN STARTUP EVENT ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    Database setup and initial data seeding are managed here.
    """
    # Calls the extracted setup function
    await init_db.run_app_setup(AsyncSessionLocal, num_users=15)
    
    print("--- Application startup complete. ---")
    yield
    print("--- Application shutting down. ---")
# ------------------------------

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan 
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(feel_lucky_game.router) 
app.include_router(users.router) 
app.include_router(realtime.router)

@app.get("/")
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Welcome endpoint that renders an HTML page, fetching sorted users 
    for the leaderboard using the service layer.
    """
    sorted_users = await services.get_sorted_leaderboard_users(db)
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "users": sorted_users}
    )
