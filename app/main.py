"""
Main entry point and configuration for the application.
"""
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Final, AsyncGenerator 

from app import init_db
from app import services
from app.settings import settings 
from app.routers import feel_lucky_game, users
from app.routers import realtime
from app.database import AsyncSessionLocal, get_db


templates: Final[Jinja2Templates] = Jinja2Templates(directory="app/templates")
"""Jinja2 template engine instance configured to load templates from 'app/templates'."""

# --- LIFESPAN STARTUP EVENT ---
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handles application startup and shutdown events gracefully.

    On startup, it ensures the database is set up and seeded.
    On shutdown, it performs any necessary cleanup operations.

    Args:
        app: The main FastAPI application instance.

    Yields:
        None: Control yields back to the application after startup.
    """
    print("--- Starting Application Setup ---")
    
    # Calls the extracted setup function (database creation and seeding)
    await init_db.run_app_setup(AsyncSessionLocal, num_users=15)
        
    print("--- Application startup complete. ---")
    yield
    
    print("--- Application shutting down. ---")
# ------------------------------

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION, 
    lifespan=lifespan 
)
"""
The main FastAPI application instance.
"""

app.mount("/static", StaticFiles(directory="app/static"), name="static")
"""Mounts the 'app/static' directory under the /static URL path for serving static assets."""

# Include API Routers
app.include_router(feel_lucky_game.router) 
app.include_router(users.router) 
app.include_router(realtime.router)
"""Includes the dedicated routers for the game, user management, and real-time features."""


@app.get("/")
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Renders the welcome page and fetches the user leaderboard.

    Args:
        request: The incoming **HTTP request object**. Required by Jinja2 templates.
        db: The **AsyncSession** dependency for database access.

    Returns:
        TemplateResponse: The rendered **index.html** page with the user leaderboard.
    """
    sorted_users = await services.get_sorted_leaderboard_users(db)
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "users": sorted_users}
    )