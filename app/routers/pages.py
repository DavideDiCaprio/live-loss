import random
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Endpoint to serve the main page.
    """
    context = {"request": request, "title": "Welcome"}
    return templates.TemplateResponse("index.html", context)


@router.get("/test-user-data", response_class=JSONResponse)
async def get_test_user_data(request: Request):
    """
    Endpoint to get the test user's data and the list of games.
    Stats are randomized on each request.
    """
    # Access the user created in app/main.py
    user: User = request.app.state.test_user
    
    # Randomize stats for the response
    user.credit = random.randint(50, 500)
    user.gambling_losses = random.randint(100, 1000)

    games = ['poker', 'slot', 'russian roulette']
    
    return {
        "user_stats": user.dict(),
        "games": games
    }
