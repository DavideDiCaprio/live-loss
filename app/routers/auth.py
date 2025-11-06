from fastapi import (
    APIRouter, 
    Depends, 
    Request, 
    Response, 
    status,
    Form
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Final, Optional

from .. import crud, security
from ..database import get_db

router = APIRouter(
    tags=["Authentication"]
)

# We need access to the templates
templates: Final[Jinja2Templates] = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request, error: Optional[str] = None):
    """
    Serves the login.html page.
    """
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "error": error}
    )

@router.post("/login")
async def login_for_user(
    request: Request, 
    response: Response, 
    db: AsyncSession = Depends(get_db),
    username: str = Form(...), # This is the email
    password: str = Form(...)
):
    """
    Processes the login form.
    """
    user = await crud.get_user_by_email(db, email=username)
    
    # Check if user exists and password is correct
    if not user or not security.verify_password(password, user.hashed_password):
        # Failed login. Redirect back to login page with an error.
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid email or password."},
            status_code=status.HTTP_400_UNAUTHORIZED
        )

    # --- Login Successful ---
    # Set a secure, HTTP-only cookie
    response.set_cookie(
        key="user_id",
        value=str(user.id),
        httponly=True,  # Makes it inaccessible to JavaScript
        samesite="strict", # Protects against CSRF
        max_age=60*60*24 # Cookie lasts for 1 day
    )
    
    # Redirect to the main game page
    # We use 303_SEE_OTHER for POST-redirect-GET pattern
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
async def logout(response: Response):
    """
    Logs the user out by deleting the cookie.
    """
    response.delete_cookie(key="user_id")
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)