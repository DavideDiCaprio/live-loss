"""
Main entry point and configuration for the application.
"""
from fastapi import Cookie, Response
from fastapi.responses import RedirectResponse
from typing import Optional
from fastapi import FastAPI, Request, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Final, AsyncGenerator 

from app import init_db
from app import services
from app.settings import settings 
from app.routers import feel_lucky_game, users, realtime, auth
from app.database import AsyncSessionLocal, get_db
from app import crud 

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
app.include_router(auth.router)
app.include_router(feel_lucky_game.router) 
app.include_router(users.router) 
app.include_router(realtime.router)
"""Includes the dedicated routers for the game, user management, and real-time features."""

@app.get("/") 
async def read_root(
    request: Request, 
    response: Response,
    db: AsyncSession = Depends(get_db),
    user_id: Optional[str] = Cookie(None)
):
    """
    Renders the welcome page and fetches the user leaderboard.

    Args:
        request: The incoming **HTTP request object**. Required by Jinja2 templates.
        db: The **AsyncSession** dependency for database access.

    Returns:
        TemplateResponse: The rendered **index.html** page with the user leaderboard.
    """

    # --- ADD THIS AUTHENTICATION CHECK ---
    if user_id is None:
        # No cookie, redirect to login page
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    try:
        current_user = await crud.get_user(db, user_id=int(user_id))
    except (ValueError, TypeError):
        current_user = None

    if current_user is None:
        # Invalid or expired cookie
        response.delete_cookie(key="user_id")
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    # --- END OF AUTH CHECK ---

    sorted_users = await services.get_sorted_leaderboard_users(db)
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "users": sorted_users, "current_user": current_user}
    )