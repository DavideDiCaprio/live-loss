from fastapi import (
    APIRouter, 
    Depends, 
    Request, 
    # Response,  <-- We no longer need this injected in the login function
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
    # response: Response, <-- REMOVED from parameters
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
    
    # 1. Create the redirect response FIRST
    redirect_response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # 2. Set the cookie on THAT response object
    redirect_response.set_cookie(
        key="user_id",
        value=str(user.id),
        httponly=True,  # Makes it inaccessible to JavaScript
        samesite="strict", # Protects against CSRF
        max_age=60*60*24 # Cookie lasts for 1 day
    )
    
    # 3. Return the response that has the cookie
    return redirect_response

@router.get("/logout")
async def logout(): # <-- REMOVED response from parameters
    """
    Logs the user out by deleting the cookie.
    """
    # 1. Create the redirect response
    redirect_response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # 2. Delete the cookie on THAT response
    redirect_response.delete_cookie(key="user_id")
    
    # 3. Return the response
    return redirect_response